# Package Distribution

This project is available as both Docker images and Python packages through GitHub Packages and Releases.

## Docker Image

### Quick Start
```bash
# Pull the latest version
docker pull ghcr.io/ahmertsengol/face-auth-opencv:latest

# Run the container
docker run -d \
  --name face-recognition \
  -p 8000:8000 \
  -v face_data:/app/data \
  ghcr.io/ahmertsengol/face-auth-opencv:latest
```

### Docker Compose
```bash
# Clone repository
git clone https://github.com/ahmertsengol/face-auth-opencv.git
cd face-auth-opencv

# Start with Docker Compose
docker-compose up -d
```

### Available Tags
- `latest` - Latest stable release
- `v2.2.4` - Specific version
- `main` - Development branch
- `sha-xxxxxxx` - Specific commit

## Python Package

### Installation from GitHub Releases
```bash
# Download from releases
wget https://github.com/ahmertsengol/face-auth-opencv/releases/download/v2.2.4/face_recognition_system-2.2.0-py3-none-any.whl

# Install the wheel
pip install face_recognition_system-2.2.0-py3-none-any.whl
```

### Development Installation
```bash
# Install from source
pip install git+https://github.com/ahmertsengol/face-auth-opencv.git
```

### Programmatic Usage
```python
from core.face_detector import FaceDetector
from core.face_recognizer import FaceRecognizer
from core.user_manager import UserManager

# Initialize components
detector = FaceDetector()
recognizer = FaceRecognizer()
user_manager = UserManager()

# Detect faces in an image
faces = detector.detect_faces("path/to/image.jpg")

# Recognize faces
results = recognizer.recognize_faces("path/to/image.jpg")
```

### CLI Usage
```bash
# Start web server
face-recognition-server --host 0.0.0.0 --port 8000

# CLI recognition
face-recognition-cli --image path/to/image.jpg
```

## Package Information

| Package Type | Latest Version | Size | Status |
|-------------|---------------|------|---------|
| Docker Image | v2.2.4 | ~800MB | ✅ Published |
| Python Package | v2.2.0 | ~50MB | ✅ Published |

## Configuration

### Environment Variables
```bash
# Production mode
FACE_RECOGNITION_ENV=production

# Log level
LOG_LEVEL=info

# Database path
DB_PATH=/app/data/face_encodings

# Upload directory
UPLOAD_DIR=/app/static/uploads
```

### Volume Mapping
```bash
# Data persistence
-v face_data:/app/data

# Log persistence  
-v face_logs:/app/logs

# Upload persistence
-v face_uploads:/app/static/uploads
```

## Features Included

### Docker Image Contents
- FastAPI web server with async support
- Modern web dashboard with live recognition
- Camera capture functionality
- Real-time analytics and monitoring
- Security - runs as non-root user
- Health checks built-in
- Multi-arch support (AMD64 + ARM64)

### Python Package Contents
- Core face detection and recognition modules
- User management system
- High-level APIs for easy integration
- CLI tools for batch processing
- Comprehensive documentation
- Unit tests included

## Updates

### Docker Image
```bash
# Pull latest version
docker pull ghcr.io/ahmertsengol/face-auth-opencv:latest

# Restart container
docker-compose pull && docker-compose up -d
```

### Python Package
```bash
# Download latest release
# Visit: https://github.com/ahmertsengol/face-auth-opencv/releases

# Install updated package
pip install --upgrade /path/to/new/wheel/file.whl
```

## Registry Information

### Docker Registry
- **Registry**: GitHub Container Registry (ghcr.io)
- **Repository**: `ghcr.io/ahmertsengol/face-auth-opencv`
- **Visibility**: Public
- **Multi-platform**: AMD64, ARM64

### Python Distribution
- **Method**: GitHub Releases
- **Format**: Python Wheel (.whl) and Source Distribution (.tar.gz)
- **Visibility**: Public
- **Download**: Direct from releases page

## Support

### Documentation
- **Installation Guide**: [INSTALLATION.md](INSTALLATION.md)
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **API Documentation**: Available at `/docs` endpoint

### Community
- **Issues**: [GitHub Issues](https://github.com/ahmertsengol/face-auth-opencv/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ahmertsengol/face-auth-opencv/discussions)
- **Releases**: [GitHub Releases](https://github.com/ahmertsengol/face-auth-opencv/releases)

## License

MIT License - See [LICENSE](LICENSE) for full details.

---

**Enterprise-ready distribution with professional deployment options** 