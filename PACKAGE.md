# Package Distribution

Available as Docker images and Python packages through GitHub.

## Docker Image

### Quick Start
```bash
# Latest version
docker pull ghcr.io/ahmertsengol/face-auth-opencv:latest
docker run -p 8000:8000 ghcr.io/ahmertsengol/face-auth-opencv:latest
```

### Docker Compose
```yaml
version: '3.8'
services:
  face-recognition:
    image: ghcr.io/ahmertsengol/face-auth-opencv:latest
    ports:
      - "8000:8000"
    volumes:
      - face_data:/app/data
```

### Available Tags
- `latest` - Latest stable
- `v2.2.4` - Specific version
- `main` - Development
- `sha-xxxxxxx` - Specific commit

## Python Package

### From GitHub Releases
```bash
# Download latest release
wget https://github.com/ahmertsengol/face-auth-opencv/releases/latest/download/face_recognition_system-2.2.0-py3-none-any.whl

# Install
pip install face_recognition_system-2.2.0-py3-none-any.whl
```

### From Source
```bash
git clone https://github.com/ahmertsengol/face-auth-opencv.git
cd face-auth-opencv
pip install -e .
```

## Usage Examples

### Docker with Volume
```bash
docker run -d \
  --name face-recognition \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  ghcr.io/ahmertsengol/face-auth-opencv:latest
```

### Python Import
```python
from face_recognition_system import FaceRecognizer

recognizer = FaceRecognizer()
result = recognizer.recognize_image("path/to/image.jpg")
```

## Configuration

### Environment Variables
```bash
FACE_RECOGNITION_ENV=production
LOG_LEVEL=info
UPLOAD_DIR=/app/uploads
```

### Docker Override
```bash
docker run -e FACE_RECOGNITION_ENV=production \
  -p 8000:8000 \
  ghcr.io/ahmertsengol/face-auth-opencv:latest
```

## Version History

- **v2.2.4** - Production web dashboard
- **v2.2.3** - Performance optimizations
- **v2.2.2** - Docker multi-platform
- **v2.2.1** - API improvements

## Package Information

| Package Type | Latest Version | Size | Status |
|-------------|---------------|------|---------|
| Docker Image | v2.2.4 | ~800MB | ✅ Published |
| Python Package | v2.2.0 | ~50MB | ✅ Published |

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