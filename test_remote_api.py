#!/usr/bin/env python3
"""
Interactive GUI-Actor API test script with OpenCV display
"""

import requests
import json
import base64
from PIL import Image
import io
import os
from datetime import datetime
import cv2
import numpy as np

# API endpoint
BASE_URL = "https://1s5bwa3j8h2jar-8080.proxy.runpod.net"

def test_health():
    """Test the health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_root():
    """Test the root endpoint"""
    print("\n🔍 Testing root endpoint...")
    try:
        response = requests.get(BASE_URL, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False

def take_screenshot():
    """Take a screenshot of the current screen"""
    try:
        import pyautogui
        screenshot = pyautogui.screenshot()
        return screenshot
    except ImportError:
        print("⚠️  pyautogui not available, creating test image instead")
        return create_test_image()
    except Exception as e:
        print(f"⚠️  Screenshot failed: {e}, creating test image instead")
        return create_test_image()

def create_test_image():
    """Create a simple test image"""
    # Create a simple test image (100x100 pixels with text)
    img = Image.new('RGB', (100, 100), color='white')
    from PIL import ImageDraw, ImageFont
    
    draw = ImageDraw.Draw(img)
    # Try to use a default font
    try:
        font = ImageFont.load_default()
    except:
        font = None
    
    draw.text((10, 40), "Test", fill='black', font=font)
    draw.rectangle([20, 20, 80, 80], outline='red', width=2)
    
    return img

def save_result_images(result, output_prefix="output"):
    """Save the result images to files"""
    # Create output directory
    os.makedirs("api_results", exist_ok=True)
    
    # Save image with point
    if result.get('image_with_point'):
        img_data = base64.b64decode(result['image_with_point'].split(',')[1])
        output_path = f"api_results/{output_prefix}_with_point.png"
        with open(output_path, 'wb') as f:
            f.write(img_data)
        print(f"✅ Saved image with point to {output_path}")
    
    # Save attention map
    if result.get('attention_map'):
        img_data = base64.b64decode(result['attention_map'].split(',')[1])
        output_path = f"api_results/{output_prefix}_attention_map.png"
        with open(output_path, 'wb') as f:
            f.write(img_data)
        print(f"✅ Saved attention map to {output_path}")

def base64_to_cv2(base64_string):
    """Convert base64 image string to OpenCV format"""
    if not base64_string:
        return None
    
    # Remove data URL prefix if present
    if base64_string.startswith('data:image'):
        base64_string = base64_string.split(',')[1]
    
    # Decode base64
    img_data = base64.b64decode(base64_string)
    
    # Convert to PIL Image
    pil_image = Image.open(io.BytesIO(img_data))
    
    # Convert PIL to OpenCV format (RGB to BGR)
    cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    
    return cv_image

def display_results(original_image, result_image, attention_map, coordinates):
    """Display results using OpenCV"""
    # Convert PIL image to OpenCV format
    original_cv = cv2.cvtColor(np.array(original_image), cv2.COLOR_RGB2BGR)
    
    # Convert result images
    result_cv = base64_to_cv2(result_image)
    
    # Handle case where attention_map might be None (fast mode)
    if attention_map is not None:
        attention_cv = base64_to_cv2(attention_map)
    else:
        attention_cv = None
    
    # Resize images to fit screen
    height, width = original_cv.shape[:2]
    max_height = 600
    max_width = 800
    
    if height > max_height or width > max_width:
        scale = min(max_height / height, max_width / width)
        new_width = int(width * scale)
        new_height = int(height * scale)
        original_cv = cv2.resize(original_cv, (new_width, new_height))
        if result_cv is not None:
            result_cv = cv2.resize(result_cv, (new_width, new_height))
        if attention_cv is not None:
            attention_cv = cv2.resize(attention_cv, (new_width, new_height))
    
    # Create display window
    cv2.namedWindow('GUI-Actor Results', cv2.WINDOW_NORMAL)
    
    # Combine images horizontally
    images = [original_cv]
    titles = ['Original Screenshot']
    
    if result_cv is not None:
        images.append(result_cv)
        titles.append('With Click Point')
    
    if attention_cv is not None:
        images.append(attention_cv)
        titles.append('Attention Map')
    
    # Create combined image
    combined = np.hstack(images)
    
    # Add text overlay
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    thickness = 2
    color = (255, 255, 255)
    
    # Add coordinates text
    coord_text = f"Coordinates: {coordinates}"
    cv2.putText(combined, coord_text, (10, 30), font, font_scale, color, thickness)
    
    # Add titles
    title_y = combined.shape[0] - 20
    for i, title in enumerate(titles):
        x = i * (combined.shape[1] // len(titles)) + 10
        cv2.putText(combined, title, (x, title_y), font, 0.5, color, 1)
    
    # Display image
    cv2.imshow('GUI-Actor Results', combined)
    
    print("\n📺 Displaying results in OpenCV window...")
    # cv2.destroyAllWindows()
    cv2.waitKey(1)

def test_process_with_base64():
    """Test the process endpoint with file upload"""
    print("\n🔍 Testing process endpoint with file upload...")
    
    # Take screenshot or create test image
    test_image = take_screenshot()
    
    # Save original screenshot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    screenshot_path = f"api_results/screenshot_{timestamp}.png"
    os.makedirs("api_results", exist_ok=True)
    test_image.save(screenshot_path)
    print(f"📸 Saved screenshot to {screenshot_path}")
    
    # Save to temporary file for upload
    temp_file = "temp_test_image.png"
    test_image.save(temp_file)
    
    try:
        with open(temp_file, 'rb') as f:
            files = {'image': ('test_image.png', f, 'image/png')}
            data = {'instruction': 'Click on the red rectangle'}
            
            response = requests.post(
                f"{BASE_URL}/process",
                files=files,
                data=data,
                timeout=30
            )
        
        # Clean up temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Process successful!")
            print(f"Coordinates: {result.get('coordinates', 'N/A')}")
            print(f"Raw coordinates: {result.get('raw_coordinates', 'N/A')}")
            print(f"Image size: {result.get('image_size', 'N/A')}")
            print(f"Image with point (base64 length): {len(result.get('image_with_point', ''))}")
            print(f"Attention map (base64 length): {len(result.get('attention_map', ''))}")
            
            # Save result images
            save_result_images(result, f"result_{timestamp}")
            
        else:
            print(f"❌ Process failed: {response.text}")
            
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Process request failed: {e}")
        # Clean up temp file on error
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return False

def test_process_with_file():
    """Test the process endpoint with file upload"""
    print("\n🔍 Testing process endpoint with file upload...")
    
    # Take screenshot or create test image
    test_image = take_screenshot()
    
    # Save to temporary file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_file = f"api_results/upload_test_{timestamp}.png"
    os.makedirs("api_results", exist_ok=True)
    test_image.save(temp_file)
    
    try:
        with open(temp_file, 'rb') as f:
            files = {'image': ('upload_test.png', f, 'image/png')}
            data = {'instruction': 'Click on the red rectangle'}
            
            response = requests.post(
                f"{BASE_URL}/process",
                files=files,
                data=data,
                timeout=30
            )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Process successful!")
            print(f"Coordinates: {result.get('coordinates', 'N/A')}")
            print(f"Raw coordinates: {result.get('raw_coordinates', 'N/A')}")
            print(f"Image size: {result.get('image_size', 'N/A')}")
            
            # Save result images
            save_result_images(result, f"upload_result_{timestamp}")
        else:
            print(f"❌ Process failed: {response.text}")
            
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Process request failed: {e}")
        return False

def test_error_handling():
    """Test error handling with invalid requests"""
    print("\n🔍 Testing error handling...")
    
    # Test with invalid image
    try:
        response = requests.post(
            f"{BASE_URL}/process-base64",
            data={'image_base64': 'invalid_base64', 'instruction': 'test'},
            timeout=10
        )
        print(f"Invalid image - Status: {response.status_code}")
    except Exception as e:
        print(f"Invalid image - Error: {e}")
    
    # Test with missing parameters
    try:
        response = requests.post(
            f"{BASE_URL}/process-base64",
            data={'instruction': 'test only'},
            timeout=10
        )
        print(f"Missing image - Status: {response.status_code}")
    except Exception as e:
        print(f"Missing image - Error: {e}")

def process_screenshot_with_instruction(screenshot, instruction, fast_mode=False):
    """Process a screenshot with a given instruction"""
    # Save screenshot to temporary file
    temp_file = "temp_screenshot.png"
    screenshot.save(temp_file)
    
    # Print debug info
    print(f"📐 Image size: {screenshot.size}")
    print(f"📁 Temp file size: {os.path.getsize(temp_file)} bytes")
    
    try:
        with open(temp_file, 'rb') as f:
            # Use proper file upload format with filename
            files = {'image': ('screenshot.png', f, 'image/png')}
            data = {'instruction': instruction, 'fast_mode': fast_mode}
            
            print(f"📤 Sending request to {BASE_URL}/process")
            response = requests.post(
                f"{BASE_URL}/process",
                files=files,
                data=data,
                timeout=30
            )
        
        # Clean up temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        # Clean up temp file on error
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return None



def speed_test_loop():
    """Speed test loop for processing multiple instructions quickly"""
    print("🚀 GUI-Actor Speed Test")
    print("=" * 50)
    
    # Check API health first
    if not test_health():
        print("❌ API is not responding. Exiting.")
        return
    
    print("✅ API is ready!")
    
    # Take screenshot once
    print("📸 Taking screenshot...")
    current_screenshot = take_screenshot()
    
    # Test instructions
    test_instructions = [
        "click on the red button",
        "find the search box",
        "click the close button",
        "click on the menu",
        "find the login button",
        "click on the settings",
        "find the submit button",
        "click on the help icon",
        "find the download link",
        "click on the profile"
    ]
    
    print(f"🔄 Running speed test with {len(test_instructions)} instructions...")
    print("=" * 50)
    
    start_time = datetime.now()
    successful_requests = 0
    
    for i, instruction in enumerate(test_instructions, 1):
        try:
            print(f"\n[{i}/{len(test_instructions)}] 🤖 Processing: '{instruction}'")
            
            # Process screenshot with instruction (fast mode for speed test)
            result = process_screenshot_with_instruction(current_screenshot, instruction, fast_mode=True)
            
            if result:
                coordinates = result.get('coordinates', 'N/A')
                print(f"✅ Success! Coordinates: {coordinates}")
                successful_requests += 1
                
                # Display with OpenCV (briefly) - handle fast mode
                attention_map = result.get('attention_map')  # Will be None in fast mode
                display_results(
                    current_screenshot,
                    result.get('image_with_point'),
                    attention_map,
                    coordinates
                )
            else:
                print("❌ Failed to process")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()
    
    print("\n" + "=" * 50)
    print("📊 Speed Test Results:")
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Successful requests: {successful_requests}/{len(test_instructions)}")
    print(f"Success rate: {(successful_requests/len(test_instructions)*100):.1f}%")
    print(f"Average time per request: {total_time/len(test_instructions):.2f} seconds")
    print(f"Requests per second: {len(test_instructions)/total_time:.2f}")

def main():
    """Main function - choose between interactive mode and speed test"""
    print("GUI-Actor API Testing")
    print("1. Interactive mode")
    print("2. Speed test")
    
    choice = input("Choose mode (1 or 2): ").strip()
    
    if choice == "2":
        speed_test_loop()
    else:
        # Interactive mode
        print("🚀 GUI-Actor Interactive API Testing")
        print("=" * 50)
        
        # Check API health first
        if not test_health():
            print("❌ API is not responding. Exiting.")
            return
        
        print("✅ API is ready!")
        print("\nCommands:")
        print("  'screenshot' - Take a new screenshot")
        print("  'quit' or 'exit' - Exit the program")
        print("  Any other text - Use as instruction for current screenshot")
        print("=" * 50)
        
        current_screenshot = None
        
        while True:
            try:
                # Get user input
                user_input = input("\n🎯 Enter instruction (or command): ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                elif user_input.lower() == 'screenshot':
                    print("📸 Taking new screenshot...")
                    current_screenshot = take_screenshot()
                    
                    # Save screenshot
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    screenshot_path = f"api_results/screenshot_{timestamp}.png"
                    os.makedirs("api_results", exist_ok=True)
                    current_screenshot.save(screenshot_path)
                    print(f"✅ Screenshot saved: {screenshot_path}")
                    
                    # Show screenshot info
                    width, height = current_screenshot.size
                    print(f"📐 Screenshot size: {width}x{height}")
                    continue
                
                elif not user_input:
                    print("⚠️  Please enter an instruction or command.")
                    continue
                
                # Process screenshot with instruction
                if current_screenshot is None:
                    print("📸 Taking screenshot first...")
                    current_screenshot = take_screenshot()
                
                print(f"🤖 Processing: '{user_input}'")
                result = process_screenshot_with_instruction(current_screenshot, user_input)
                
                # If screenshot fails, try with a test image
                if result is None:
                    print("⚠️  Screenshot processing failed, trying with test image...")
                    test_image = create_test_image()
                    result = process_screenshot_with_instruction(test_image, user_input)
                
                if result:
                    coordinates = result.get('coordinates', 'N/A')
                    raw_coords = result.get('raw_coordinates', {})
                    
                    print(f"✅ Success! Coordinates: {coordinates}")
                    if raw_coords:
                        print(f"📍 Raw coordinates: x={raw_coords.get('x', 'N/A'):.4f}, y={raw_coords.get('y', 'N/A'):.4f}")
                    
                    # Save results
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    save_result_images(result, f"interactive_{timestamp}")
                    
                    # Display with OpenCV
                    display_results(
                        current_screenshot,
                        result.get('image_with_point'),
                        result.get('attention_map'),
                        coordinates
                    )
                else:
                    print("❌ Failed to process screenshot")
                    
            except KeyboardInterrupt:
                print("\n👋 Interrupted by user. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 
