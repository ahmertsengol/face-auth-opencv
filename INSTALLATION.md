# Installation Guide

Quick setup instructions for the Face Recognition System.

## Requirements

- **Python**: 3.10+
- **Camera**: USB webcam or built-in
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space

## Quick Install

### Docker (Recommended)
```bash
docker run -p 8000:8000 ghcr.io/ahmertsengol/face-auth-opencv:latest
```

### From Source
```bash
git clone https://github.com/ahmertsengol/face-auth-opencv.git
cd face-auth-opencv
make install
```

## Platform Setup

### macOS
```bash
# Install Homebrew (if needed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install cmake
```

### Ubuntu/Linux
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv cmake build-essential
```

### Windows
```powershell
# Install Python 3.10+ from python.org
# Install Visual Studio Build Tools
# Then run the setup
```

## Manual Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install requirements
pip install -r config/requirements.txt

# Start server
uvicorn api.main:app --reload
```

## Verification

```bash
# Test installation
python -c "import cv2, face_recognition; print('✅ All dependencies installed')"

# Check web interface
curl http://localhost:8000/api/health
```

## Troubleshooting

**Installation Fails**
```bash
# Update pip and try again
pip install --upgrade pip
pip install -r config/requirements.txt
```

**Camera Issues**
```bash
# Test camera access
python -c "import cv2; cap = cv2.VideoCapture(0); print('✅ Camera OK' if cap.read()[0] else '❌ Camera Error')"
```

**Performance Issues**
```bash
# Install with optimizations
pip install opencv-python-headless
```

## Next Steps

1. Open `http://localhost:8000`
2. Add your first user
3. Test recognition
4. Check [Quick Start Guide](QUICKSTART.md) 