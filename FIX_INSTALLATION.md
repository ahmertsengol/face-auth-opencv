# Installation Troubleshooting

Quick solutions for common installation problems.

## Missing face_recognition_models Error

**Error Message:**
```
Please install `face_recognition_models` with this command before using `face_recognition`:
pip install git+https://github.com/ageitgey/face_recognition_models
```

### Quick Fix
```bash
# Install the missing package
pip install git+https://github.com/ageitgey/face_recognition_models

# Retry the test
make test

# Verify system status
make status
```

## Complete Reinstallation

If the quick fix doesn't work:

```bash
# Reinstall all requirements
pip install -r config/requirements.txt

# Install face_recognition_models separately
pip install git+https://github.com/ageitgey/face_recognition_models

# Run system test
make test

# Run performance benchmark
make benchmark
```

## Verification Checklist

- ✅ Python 3.10+ installed
- ✅ Virtual environment active
- ✅ requirements.txt installed
- ✅ face_recognition_models installed
- ✅ Camera access granted

## Quick Test

```bash
# Test Python imports
python -c "
import face_recognition
import cv2
import numpy as np
print('✅ All packages installed successfully!')
"

# Run system diagnostics
make test

# Start the system
make register
```

## If Problems Persist

### Option 1: Clean Virtual Environment
```bash
# Remove and recreate environment
make clean-venv
make install
```

### Option 2: Manual Installation
```bash
# Install core packages manually
pip install dlib
pip install face-recognition
pip install git+https://github.com/ageitgey/face_recognition_models
```

### Option 3: Docker Alternative
```bash
# Use Docker instead
docker pull ghcr.io/ahmertsengol/face-auth-opencv:latest
docker run -p 8000:8000 -v face_data:/app/data ghcr.io/ahmertsengol/face-auth-opencv:latest
```

## Common Issues

### Camera Permission Denied
```bash
# macOS: System Preferences → Security & Privacy → Camera
# Linux: sudo usermod -a -G video $USER
# Windows: Settings → Privacy → Camera
```

### CMake Errors (macOS)
```bash
# Install/reinstall CMake
brew install cmake
pip uninstall dlib
pip install dlib
```

### Import Errors
```bash
# Check installed packages
pip list | grep -E "(opencv|face-recognition|dlib)"

# Reinstall problematic packages
pip install --upgrade opencv-python face-recognition
```

### Memory Issues
```bash
# Clear cache and optimize
make optimize

# Check available memory
free -h  # Linux
vm_stat  # macOS
```

## Getting Additional Help

1. **Check Documentation**: [INSTALLATION.md](INSTALLATION.md)
2. **Review Logs**: `cat logs/app.log`
3. **Report Issues**: [GitHub Issues](https://github.com/ahmertsengol/face-auth-opencv/issues)
4. **Community Support**: [GitHub Discussions](https://github.com/ahmertsengol/face-auth-opencv/discussions)

---

**✅ Your face recognition system should now be working correctly!** 