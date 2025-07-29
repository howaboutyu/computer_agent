import base64
import os
import json
import torch
from typing import Optional
from PIL import Image, ImageDraw
import numpy as np
import matplotlib.pyplot as plt
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import io
from qwen_vl_utils import process_vision_info
from datasets import load_dataset
from transformers import AutoProcessor
from gui_actor.constants import chat_template
from gui_actor.modeling_qwen25vl import Qwen2_5_VLForConditionalGenerationWithPointer
from gui_actor.inference import inference

MAX_PIXELS = 3200 * 1800

app = FastAPI(
    title="GUI-Actor API",
    description="Coordinate-Free Visual Grounding for GUI Agents",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def resize_image(image, resize_to_pixels=MAX_PIXELS):
    image_width, image_height = image.size
    if (resize_to_pixels is not None) and ((image_width * image_height) != resize_to_pixels):
        resize_ratio = (resize_to_pixels / (image_width * image_height)) ** 0.5
        image_width_resized, image_height_resized = int(image_width * resize_ratio), int(image_height * resize_ratio)
        image = image.resize((image_width_resized, image_height_resized))
    return image

@torch.inference_mode()
def draw_point(image: Image.Image, point: list, radius=8, color=(255, 0, 0, 128)):
    overlay = Image.new('RGBA', image.size, (255, 255, 255, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    x, y = point
    overlay_draw.ellipse(
        [(x - radius, y - radius), (x + radius, y + radius)],
        outline=color,
        width=5  # Adjust thickness as needed
    )
    image = image.convert('RGBA')
    combined = Image.alpha_composite(image, overlay)
    combined = combined.convert('RGB')
    return combined

@torch.inference_mode()
def get_attn_map(image, attn_scores, n_width, n_height):
    w, h = image.size
    scores = np.array(attn_scores[0]).reshape(n_height, n_width)

    scores_norm = (scores - scores.min()) / (scores.max() - scores.min())
    # Resize score map to match image size
    score_map = Image.fromarray((scores_norm * 255).astype(np.uint8)).resize((w, h), resample=Image.NEAREST) # BILINEAR)
    # Apply colormap
    colormap = plt.get_cmap('jet')
    colored_score_map = colormap(np.array(score_map) / 255.0)  # returns RGBA
    colored_score_map = (colored_score_map[:, :, :3] * 255).astype(np.uint8)
    colored_overlay = Image.fromarray(colored_score_map)

    # Blend with original image
    blended = Image.blend(image, colored_overlay, alpha=0.3)
    return blended

# Global model variables
model = None
tokenizer = None
data_processor = None

def load_model():
    """Load the model globally"""
    global model, tokenizer, data_processor
    
    if torch.cuda.is_available():
        model_name_or_path = "microsoft/GUI-Actor-7B-Qwen2.5-VL"
        data_processor = AutoProcessor.from_pretrained(model_name_or_path)
        tokenizer = data_processor.tokenizer
        model = Qwen2_5_VLForConditionalGenerationWithPointer.from_pretrained(
            model_name_or_path,
            torch_dtype=torch.bfloat16,
            device_map="cuda:0",
            attn_implementation="flash_attention_2"
        ).eval()
    else:
        model_name_or_path = "microsoft/GUI-Actor-3B-Qwen2.5-VL"
        data_processor = AutoProcessor.from_pretrained(model_name_or_path)
        tokenizer = data_processor.tokenizer
        model = Qwen2_5_VLForConditionalGenerationWithPointer.from_pretrained(
            model_name_or_path,
            torch_dtype=torch.bfloat16,
            device_map="cpu"
        ).eval()

def image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string"""
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

@torch.inference_mode()
def process(image: Image.Image, instruction: str):
    """Process the image and instruction to get predictions"""
    # resize image
    w, h = image.size
    if w * h > MAX_PIXELS:
        image = resize_image(image)

    conversation = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": "You are a GUI agent. Given a screenshot of the current GUI and a human instruction, your task is to locate the screen element that corresponds to the instruction. You should output a PyAutoGUI action that performs a click on the correct position.To indicate the click location, we will use some special tokens, which is used to refer to a visual patch later. For example, you can output: pyautogui.click(<your_special_token_here>).",
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "image": image, # PIL.Image.Image or str to path
                    # "image_url": "https://xxxxx.png" or "https://xxxxx.jpg" or "file://xxxxx.png" or "data:image/png;base64,xxxxxxxx", will be split by "base64,"
                },
                {
                    "type": "text",
                    "text": instruction,
                },
            ],
        },
    ]

    try:
        pred = inference(conversation, model, tokenizer, data_processor, use_placeholder=True, topk=3)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during inference: {str(e)}")

    px, py = pred["topk_points"][0]
    output_coord = f"({px:.4f}, {py:.4f})"
    img_with_point = draw_point(image, (px * w, py * h))

    n_width, n_height = pred["n_width"], pred["n_height"]
    attn_scores = pred["attn_scores"]
    att_map = get_attn_map(image, attn_scores, n_width, n_height)

    return {
        "image_with_point": image_to_base64(img_with_point),
        "coordinates": output_coord,
        "attention_map": image_to_base64(att_map),
        "raw_coordinates": {"x": px, "y": py},
        "image_size": {"width": w, "height": h}
    }

@app.on_event("startup")
async def startup_event():
    """Load model on startup"""
    load_model()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "GUI-Actor API",
        "description": "Coordinate-Free Visual Grounding for GUI Agents",
        "endpoints": {
            "/process": "POST - Process image and instruction",
            "/health": "GET - Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "cuda_available": torch.cuda.is_available()
    }

@app.post("/process")
async def process_image(
    image: UploadFile = File(...),
    instruction: str = Form(...)
):
    """
    Process an image with an instruction to locate GUI elements
    
    Args:
        image: Uploaded image file
        instruction: Text instruction describing what to find
    
    Returns:
        JSON response with processed results
    """
    # Validate file type
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read and convert image
        image_data = await image.read()
        pil_image = Image.open(io.BytesIO(image_data)).convert('RGB')
        
        # Process the image
        result = process(pil_image, instruction)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.post("/process-base64")
async def process_base64_image(
    image_base64: str = Form(...),
    instruction: str = Form(...)
):
    """
    Process an image (base64 encoded) with an instruction
    
    Args:
        image_base64: Base64 encoded image string
        instruction: Text instruction describing what to find
    
    Returns:
        JSON response with processed results
    """
    try:
        # Decode base64 image
        if image_base64.startswith('data:image'):
            # Remove data URL prefix
            image_base64 = image_base64.split(',')[1]
        
        image_data = base64.b64decode(image_base64)
        pil_image = Image.open(io.BytesIO(image_data)).convert('RGB')
        
        # Process the image
        result = process(pil_image, instruction)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing base64 image: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080) 