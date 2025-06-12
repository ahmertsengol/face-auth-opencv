# Quick Start Guide

Get your face recognition system running in under 5 minutes.

## 1. Installation

```bash
# Docker (Fastest)
docker run -p 8000:8000 ghcr.io/ahmertsengol/face-auth-opencv:latest

# From Source
git clone https://github.com/ahmertsengol/face-auth-opencv.git
cd face-auth-opencv && make install
```

## 2. First User

**Web Interface** (Recommended):
1. Open `http://localhost:8000`
2. Click "Add New User"
3. Enter name + upload photos or use camera
4. Click "Add User"

**Command Line**:
```bash
make register  # Follow prompts
```

## 3. Start Recognition

**Web Dashboard**:
- Click "Live Recognition" or visit `/live-recognition`
- Allow camera access
- Your face will be recognized automatically

**Command Line**:
```bash
make recognize  # Opens camera window
```

## Key Features

- **Dashboard**: User management, analytics, system health
- **Live Recognition**: Full-screen camera interface
- **API**: RESTful endpoints at `/docs`
- **Themes**: Dark/light mode toggle

## Troubleshooting

```bash
# Check status
make status

# Fix common issues
make clean && make install

# Test camera
python -c "import cv2; cap = cv2.VideoCapture(0); print('✅' if cap.read()[0] else '❌')"
```

## Next Steps

- Add multiple users for testing
- Explore API documentation at `/docs`
- Check system metrics in dashboard
- Review [Installation Guide](INSTALLATION.md) for advanced setup

---

**🎉 That's it! Your face recognition system is ready to use.** 