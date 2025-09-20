#!/bin/bash

# Propaganda Spotter Web App - One-Time Setup Script
echo "🚀 Performing one-time setup for Propaganda Spotter..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

# Check if Node.js and npm are installed
if ! command -v node &> /dev/null || ! command -v npm &> /dev/null; then
    echo "❌ Node.js and npm are required but not installed."
    echo "Please install Node.js 16 or higher and try again."
    exit 1
fi

echo "✅ Prerequisites check passed."

# Setup Backend
echo "
📦 Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies (this may take a while)..."
pip install --upgrade pip
pip install -r requirements.txt

deactivate
echo "✅ Backend setup complete."

# Setup Frontend
echo "
📦 Setting up frontend..."
cd ../frontend

# Install Node.js dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies (this may take a while)..."
    npm install
else
    echo "Node.js dependencies already installed."
fi

echo "✅ Frontend setup complete."

# Return to root directory
cd ..

echo "
🎉 Setup complete!"
echo "
👉 You can now start the application by running: ./run.sh"