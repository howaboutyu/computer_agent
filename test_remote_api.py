#!/usr/bin/env python3
"""
Test script for remote GUI-Actor API
"""

import requests
import json
import base64
from PIL import Image
import io

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

def test_process_with_base64():
    """Test the process endpoint with base64 image"""
    print("\n🔍 Testing process endpoint with base64 image...")
    
    # Create test image
    test_image = create_test_image()
    
    # Convert to base64
    buffer = io.BytesIO()
    test_image.save(buffer, format='PNG')
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    # Test data
    data = {
        'image_base64': image_base64,
        'instruction': 'Click on the red rectangle'
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/process-base64",
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
            print(f"Image with point (base64 length): {len(result.get('image_with_point', ''))}")
            print(f"Attention map (base64 length): {len(result.get('attention_map', ''))}")
        else:
            print(f"❌ Process failed: {response.text}")
            
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Process request failed: {e}")
        return False

def test_process_with_file():
    """Test the process endpoint with file upload"""
    print("\n🔍 Testing process endpoint with file upload...")
    
    # Create test image
    test_image = create_test_image()
    
    # Save to temporary file
    temp_file = "test_image.png"
    test_image.save(temp_file)
    
    try:
        with open(temp_file, 'rb') as f:
            files = {'image': f}
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
        else:
            print(f"❌ Process failed: {response.text}")
            
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Process request failed: {e}")
        return False
    finally:
        # Clean up temp file
        import os
        #if os.path.exists(temp_file):
        #    os.remove(temp_file)

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

def main():
    """Run all tests"""
    print("🚀 Testing GUI-Actor API at:", BASE_URL)
    print("=" * 50)
    
    # Test basic endpoints
    health_ok = test_health()
    root_ok = test_root()
    
    if not health_ok:
        print("❌ API is not responding properly. Stopping tests.")
        return
    
    # Test processing endpoints
    base64_ok = test_process_with_base64()
    file_ok = test_process_with_file()
    
    # Test error handling
    test_error_handling()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"Health Check: {'✅' if health_ok else '❌'}")
    print(f"Root Endpoint: {'✅' if root_ok else '❌'}")
    print(f"Base64 Process: {'✅' if base64_ok else '❌'}")
    print(f"File Upload Process: {'✅' if file_ok else '❌'}")
    
    if health_ok and (base64_ok or file_ok):
        print("\n🎉 API is working correctly!")
    else:
        print("\n⚠️  Some tests failed. Check the API configuration.")

if __name__ == "__main__":
    main() 
