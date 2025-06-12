# Installation Guide

Complete installation instructions for setting up the Face Recognition System on a new machine.

## System Requirements

**Minimum Requirements**
- **OS**: macOS 10.15+, Ubuntu 18.04+, Windows 10+
- **Python**: 3.10 or higher
- **RAM**: 4GB (8GB recommended)
- **Storage**: 2GB free space
- **Camera**: USB webcam or built-in camera

## Platform-Specific Prerequisites

### macOS
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install CMake
brew install cmake
```

### Ubuntu/Linux
```bash
# Update system packages
sudo apt update

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv
sudo apt install cmake build-essential
sudo apt install libgtk-3-dev libavcodec-dev libavformat-dev libswscale-dev
```

### Windows
- Install [Python 3.10+](https://python.org/downloads)
- Install [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/)
- Install [Git for Windows](https://git-scm.com/download/win)

## Quick Installation

### Method 1: Automatic Setup (Recommended)
```bash
# Clone the repository
git clone https://github.com/ahmertsengol/face-auth-opencv.git
cd face-auth-opencv

# One-command installation
make install

# Verify installation
make test
```

### Method 2: Docker Installation
```bash
# Pull and run the Docker image
docker pull ghcr.io/ahmertsengol/face-auth-opencv:latest

# Run with volume mounting
docker run -d \
  --name face-recognition \
  -p 8000:8000 \
  -v face_data:/app/data \
  ghcr.io/ahmertsengol/face-auth-opencv:latest

# Access web interface
open http://localhost:8000
```

### Method 3: Manual Installation
```bash
# Create virtual environment
python3 -m venv venv_face_recognition
source venv_face_recognition/bin/activate  # macOS/Linux
# venv_face_recognition\Scripts\activate  # Windows

# Install dependencies
pip install --upgrade pip
pip install -r config/requirements.txt

# Verify installation
python -c "import face_recognition, cv2; print('Installation successful')"
```

## Verification

### System Health Check
```bash
# Check installation status
make status
```

**Expected Output:**
```
📊 System Status
==================
✅ Virtual Environment: Ready
  Python 3.11.9
✅ Configuration: Ready
  File: config/app_config.json
✅ Data Directory: Ready
  Users: 0
✅ Log Directory: Ready
```

### Performance Test
```bash
# Run benchmark test
make benchmark

# Expected: ~1.3ms/frame processing time
```

## First Usage

### 1. Register Your First User
```bash
# Start user registration
make register

# Follow prompts:
# - Enter name
# - Camera opens → Press 's' to capture 5 photos
# - Press 'q' to exit
```

### 2. Test Face Recognition
```bash
# Start recognition mode
make recognize

# Camera opens → Show your face → Recognition results appear
```

### 3. Web Dashboard
```bash
# Start web server
uvicorn api.main:app --reload

# Open browser: http://localhost:8000
# Use the modern web interface
```

## Camera Configuration

### macOS
- Grant camera permissions:
  - System Preferences → Security & Privacy → Camera
  - Enable access for Terminal/Python

### Linux
```bash
# Add user to video group
sudo usermod -a -G video $USER

# Logout and login again
```

### Windows
- Windows Settings → Privacy → Camera
- Allow camera access for applications

## Troubleshooting

### Camera Issues
```bash
# Test camera access
python -c "
import cv2
cap = cv2.VideoCapture(0)
if cap.isOpened():
    print('✅ Camera working')
else:
    print('❌ Camera issue')
cap.release()
"
```

### Import Errors
```bash
# Check installed packages
pip list | grep -E "(opencv|numpy|dlib|face-recognition)"

# Reinstall if missing
pip install opencv-python==4.8.1.78
pip install face-recognition
```

### CMake Errors (macOS)
```bash
# Reinstall dlib with CMake
brew install cmake
pip uninstall dlib
pip install dlib
```

### Missing face_recognition_models
```bash
# Install missing models
pip install git+https://github.com/ageitgey/face_recognition_models
```

### Memory Issues
```bash
# Clear cache and optimize
make optimize

# Reset configuration
rm -rf config/app_config.json
python -c "from config.app_config import get_config_manager; get_config_manager().save_config()"
```

### Virtual Environment Issues
```bash
# Remove and recreate environment
make clean-venv
make install
```

## Advanced Configuration

### Environment Variables
```bash
# Create .env file
cat > .env << EOF
FACE_RECOGNITION_ENV=production
LOG_LEVEL=info
DB_PATH=./data/face_encodings
UPLOAD_DIR=./static/uploads
EOF
```

### Custom Settings
```bash
# Edit configuration
nano config/app_config.json

# Key settings:
# - detection_threshold: Face detection sensitivity
# - recognition_tolerance: Recognition accuracy
# - max_faces: Maximum faces per user
```

## Performance Optimization

### Hardware Acceleration (Optional)
```bash
# Install GPU-accelerated OpenCV (if CUDA available)
pip uninstall opencv-python
pip install opencv-contrib-python
```

### Memory Optimization
```bash
# Configure for low-memory systems
export FACE_RECOGNITION_BATCH_SIZE=1
export OPENCV_LOG_LEVEL=ERROR
```

## Update and Maintenance

### Update to Latest Version
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r config/requirements.txt --upgrade

# Run tests
make test
```

### Backup Data
```bash
# Backup user data
make backup

# Backup location: ./backups/face_data_YYYYMMDD_HHMMSS.tar.gz
```

### Log Management
```bash
# View logs
make logs

# Clear old logs
find logs/ -name "*.log" -mtime +30 -delete
```

## Support

### Getting Help
- **Documentation**: Check [QUICKSTART.md](QUICKSTART.md) for quick setup
- **Issues**: Report problems on [GitHub Issues](https://github.com/ahmertsengol/face-auth-opencv/issues)
- **Discussions**: Join [GitHub Discussions](https://github.com/ahmertsengol/face-auth-opencv/discussions)

### Common Solutions
1. **Installation fails**: Try manual installation method
2. **Camera not detected**: Check permissions and drivers
3. **Poor performance**: Run `make optimize` and check system resources
4. **Import errors**: Verify all dependencies are installed

---

**Installation complete! Your face recognition system is ready to use.** 