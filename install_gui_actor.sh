#!/bin/bash

echo "Installing GUI-Actor dependencies..."

# Check if GUI-Actor directory exists
if [ ! -d "GUI-Actor" ]; then
    echo "Error: GUI-Actor directory not found. Please run:"
    echo "git submodule update --init --recursive"
    exit 1
fi

# Try to install GUI-Actor
echo "Installing GUI-Actor package..."
cd GUI-Actor

# Try to install without flash-attn first (CPU version)
echo "Attempting CPU-compatible installation..."
pip install -e . --no-deps || {
    echo "Failed to install GUI-Actor. Trying alternative approach..."
    
    # Install core dependencies manually
    pip install transformers datasets accelerate qwen-vl-utils
    
    # Try to install GUI-Actor again
    pip install -e . --no-deps || {
        echo "Warning: GUI-Actor installation failed. The API will not work properly."
        echo "You may need to install CUDA dependencies or use a different environment."
    }
}

cd ..

echo "Installation complete!"
echo ""
echo "To test the installation, run:"
echo "make health"
echo ""
echo "To start the server:"
echo "make dev" 