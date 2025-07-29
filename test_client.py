import requests
import base64
from PIL import Image
import io

# API base URL
BASE_URL = "http://localhost:8080"

def test_health():
    """Test the health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print("Health Check Response:")
    print(response.json())
    print()

def test_process_with_file(image_path: str, instruction: str):
    """Test the /process endpoint with file upload"""
    with open(image_path, 'rb') as f:
        files = {'image': f}
        data = {'instruction': instruction}
        
        response = requests.post(f"{BASE_URL}/process", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print("Process Response:")
            print(f"Coordinates: {result['coordinates']}")
            print(f"Raw coordinates: {result['raw_coordinates']}")
            print(f"Image size: {result['image_size']}")
            print(f"Image with point (base64): {result['image_with_point'][:50]}...")
            print(f"Attention map (base64): {result['attention_map'][:50]}...")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
        print()

def test_process_with_base64(image_path: str, instruction: str):
    """Test the /process-base64 endpoint with base64 encoded image"""
    # Convert image to base64
    with open(image_path, 'rb') as f:
        image_data = f.read()
        image_base64 = base64.b64encode(image_data).decode()
    
    data = {
        'image_base64': image_base64,
        'instruction': instruction
    }
    
    response = requests.post(f"{BASE_URL}/process-base64", data=data)
    
    if response.status_code == 200:
        result = response.json()
        print("Process Base64 Response:")
        print(f"Coordinates: {result['coordinates']}")
        print(f"Raw coordinates: {result['raw_coordinates']}")
        print(f"Image size: {result['image_size']}")
        print(f"Image with point (base64): {result['image_with_point'][:50]}...")
        print(f"Attention map (base64): {result['attention_map'][:50]}...")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
    print()

def save_result_images(result, output_prefix="output"):
    """Save the result images to files"""
    # Save image with point
    if result.get('image_with_point'):
        img_data = base64.b64decode(result['image_with_point'].split(',')[1])
        with open(f"{output_prefix}_with_point.png", 'wb') as f:
            f.write(img_data)
        print(f"Saved image with point to {output_prefix}_with_point.png")
    
    # Save attention map
    if result.get('attention_map'):
        img_data = base64.b64decode(result['attention_map'].split(',')[1])
        with open(f"{output_prefix}_attention_map.png", 'wb') as f:
            f.write(img_data)
        print(f"Saved attention map to {output_prefix}_attention_map.png")

if __name__ == "__main__":
    # Test health endpoint
    test_health()
    
    # Example usage (uncomment and modify as needed)
    # image_path = "path/to/your/screenshot.png"
    # instruction = "Click on the login button"
    
    # test_process_with_file(image_path, instruction)
    # test_process_with_base64(image_path, instruction)
    
    print("API Test Client")
    print("To test with your own image:")
    print("1. Update the image_path variable")
    print("2. Update the instruction variable")
    print("3. Uncomment the test function calls")
    print("4. Run the script") 