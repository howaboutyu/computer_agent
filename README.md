# GUI-Actor FastAPI

A FastAPI implementation of the GUI-Actor model for coordinate-free visual grounding of GUI agents.

## Overview

This FastAPI application provides REST API endpoints for processing GUI screenshots and natural language instructions to locate and interact with UI elements. It's based on the original Gradio implementation but converted to a production-ready API service.

## Features

- **Image Processing**: Upload images or send base64-encoded images
- **Natural Language Instructions**: Process human-readable instructions to locate UI elements
- **Coordinate Prediction**: Get precise coordinates for clicking on UI elements
- **Visual Feedback**: Receive images with highlighted click points and attention maps
- **Health Monitoring**: Built-in health check endpoints
- **CORS Support**: Cross-origin resource sharing enabled

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install GUI-Actor Dependencies**:
   ```bash
   # Clone the GUI-Actor repository if you haven't already
   git clone https://github.com/microsoft/GUI-Actor.git
   cd GUI-Actor
   pip install -e .
   ```

## Usage

### Starting the Server

```bash
python main.py
```

The server will start on `http://localhost:8080` by default.

### API Endpoints

#### 1. Health Check
```bash
GET /health
```

Returns the health status of the service and model loading status.

**Response**:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "cuda_available": true
}
```

#### 2. Process Image (File Upload)
```bash
POST /process
```

**Parameters**:
- `image`: Image file (multipart/form-data)
- `instruction`: Text instruction (form data)

**Example using curl**:
```bash
curl -X POST "http://localhost:8080/process" \
  -F "image=@screenshot.png" \
  -F "instruction=Click on the login button"
```

#### 3. Process Image (Base64)
```bash
POST /process-base64
```

**Parameters**:
- `image_base64`: Base64 encoded image string
- `instruction`: Text instruction

**Example using curl**:
```bash
curl -X POST "http://localhost:8080/process-base64" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "image_base64=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..." \
  -d "instruction=Click on the login button"
```

### Response Format

Both processing endpoints return the same JSON response:

```json
{
  "image_with_point": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "coordinates": "(0.5234, 0.6789)",
  "attention_map": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "raw_coordinates": {
    "x": 0.5234,
    "y": 0.6789
  },
  "image_size": {
    "width": 1920,
    "height": 1080
  }
}
```

**Response Fields**:
- `image_with_point`: Base64 encoded image with red circle showing the predicted click location
- `coordinates`: Formatted coordinate string
- `attention_map`: Base64 encoded attention map visualization
- `raw_coordinates`: Raw x, y coordinates (normalized 0-1)
- `image_size`: Original image dimensions

## Testing

Use the provided test client to verify the API:

```bash
python test_client.py
```

Modify the test client to use your own images and instructions.

## Model Information

The application automatically loads the appropriate model based on hardware availability:

- **CUDA Available**: Uses `microsoft/GUI-Actor-7B-Qwen2.5-VL` with flash attention
- **CPU Only**: Uses `microsoft/GUI-Actor-3B-Qwen2.5-VL`

## Configuration

### Environment Variables

- `MAX_PIXELS`: Maximum image size in pixels (default: 3200 * 1800)
- `PORT`: Server port (default: 8080)
- `HOST`: Server host (default: 0.0.0.0)

### Model Configuration

The model is loaded with the following settings:
- **CUDA**: `torch_dtype=torch.bfloat16`, `device_map="cuda:0"`, `attn_implementation="flash_attention_2"`
- **CPU**: `torch_dtype=torch.bfloat16`, `device_map="cpu"`

## Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Invalid image format or missing parameters
- **500 Internal Server Error**: Model inference errors or processing failures

## Performance Considerations

- Images are automatically resized if they exceed `MAX_PIXELS`
- The model is loaded once at startup and reused for all requests
- Inference is performed with `@torch.inference_mode()` for optimal performance

## Integration Examples

### Python Client
```python
import requests

def process_gui_image(image_path, instruction):
    with open(image_path, 'rb') as f:
        files = {'image': f}
        data = {'instruction': instruction}
        response = requests.post('http://localhost:8080/process', files=files, data=data)
        return response.json()

# Usage
result = process_gui_image('screenshot.png', 'Click the submit button')
print(f"Click at coordinates: {result['coordinates']}")
```

### JavaScript Client
```javascript
async function processGUIImage(imageFile, instruction) {
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('instruction', instruction);
    
    const response = await fetch('http://localhost:8080/process', {
        method: 'POST',
        body: formData
    });
    
    return await response.json();
}
```

## Troubleshooting

1. **Model Loading Issues**: Ensure you have sufficient RAM/VRAM for the model
2. **CUDA Errors**: Install appropriate CUDA drivers and PyTorch version
3. **Memory Issues**: Reduce `MAX_PIXELS` or use CPU-only mode
4. **Import Errors**: Ensure GUI-Actor dependencies are properly installed

## License

This project follows the same license as the original GUI-Actor repository. 