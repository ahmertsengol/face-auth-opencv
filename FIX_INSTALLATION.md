# Installation Troubleshooting

Quick solutions for common installation problems.

## Missing face_recognition_models Error

**Error:**
```
Please install `face_recognition_models` with this command:
pip install git+https://github.com/ageitgey/face_recognition_models
```

**Fix:**
```bash
pip install git+https://github.com/ageitgey/face_recognition_models
make test  # Verify fix
```

## Camera Access Issues

**Error:** Camera not detected or permission denied

**Fix:**
```bash
# Test camera
python -c "import cv2; cap = cv2.VideoCapture(0); print('✅' if cap.read()[0] else '❌')"

# macOS: Grant camera permissions in System Preferences
# Linux: Add user to video group
sudo usermod -a -G video $USER

# Windows: Enable camera access in Settings
```

## Import Errors

**Error:** ModuleNotFoundError for OpenCV, dlib, or face_recognition

**Fix:**
```bash
# Reinstall dependencies
pip install --upgrade pip
pip install -r config/requirements.txt

# For specific modules
pip install opencv-python==4.8.1.78
pip install dlib
pip install face-recognition
```

## Performance Issues

**Symptoms:** Slow recognition, high memory usage

**Fix:**
```bash
# Optimize performance
pip install opencv-python-headless  # Lighter version
make optimize  # Clear cache

# For low-memory systems
export FACE_RECOGNITION_BATCH_SIZE=1
```

## Complete Reinstall

If all else fails:
```bash
# Clean everything
make clean
rm -rf venv/

# Fresh install
make install
make test
```

## Docker Issues

**Error:** Docker build fails or container won't start

**Fix:**
```bash
# Pull pre-built image
docker pull ghcr.io/ahmertsengol/face-auth-opencv:latest

# Or build locally
docker build -t face-recognition .
docker run -p 8000:8000 face-recognition
```

## Get Help

- Check [Installation Guide](INSTALLATION.md)
- Review [Quick Start](QUICKSTART.md)
- Report issues on GitHub 