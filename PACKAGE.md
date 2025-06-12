# 📦 Face Recognition System - GitHub Packages

Bu proje için GitHub Packages'ta aşağıdaki paketler mevcuttur:

## 🐳 Docker Image

### Kullanım:
```bash
# En son sürümü çek
docker pull ghcr.io/yourusername/image_processing:latest

# Container'ı çalıştır
docker run -d \
  --name face-recognition \
  -p 8000:8000 \
  -v face_data:/app/data \
  ghcr.io/yourusername/image_processing:latest
```

### Docker Compose ile:
```bash
# Bu repository'yi klon et
git clone https://github.com/yourusername/image_processing.git
cd image_processing

# Docker Compose ile başlat
docker-compose up -d
```

### Mevcut Tag'ler:
- `latest` - En son stable sürüm
- `v2.2.0` - Specific version
- `main` - Development branch
- `sha-xxxxxxx` - Specific commit

## 🐍 Python Package

### Kurulum:
```bash
# PyPI'dan kur (henüz yayınlanmadı)
pip install face-recognition-system

# Veya development sürümü için
pip install git+https://github.com/yourusername/image_processing.git
```

### Programmatic Kullanım:
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

### CLI Kullanımı:
```bash
# Web server'ı başlat
face-recognition-server --host 0.0.0.0 --port 8000

# CLI ile kullan
face-recognition-cli --image path/to/image.jpg
```

## 📋 Mevcut Sürümler

| Package Type | Latest Version | Size | Downloads |
|-------------|---------------|------|-----------|
| Docker Image | v2.2.0 | ~800MB | ![Downloads](https://img.shields.io/docker/pulls/ghcr.io/yourusername/image_processing) |
| Python Package | v2.2.0 | ~50MB | ![Downloads](https://img.shields.io/pypi/dm/face-recognition-system) |

## 🔧 Konfigürasyon

### Environment Variables:
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

### Volume Mapping:
```bash
# Data persistence
-v face_data:/app/data

# Log persistence  
-v face_logs:/app/logs

# Upload persistence
-v face_uploads:/app/static/uploads
```

## 🚀 Özellikler

### ✅ Docker Image İçeriği:
- 🔥 **FastAPI web server** with async support
- 🎨 **Modern web dashboard** with live recognition
- 📷 **Camera capture** functionality
- 📊 **Real-time analytics** and monitoring
- 🔒 **Security** - runs as non-root user
- 🏥 **Health checks** built-in
- 📦 **Multi-arch support** (AMD64 + ARM64)

### ✅ Python Package İçeriği:
- 🧠 **Core face detection** and recognition modules
- 📚 **User management** system
- 🎯 **High-level APIs** for easy integration
- 🔧 **CLI tools** for batch processing
- 📖 **Comprehensive documentation**
- 🧪 **Unit tests** included

## 🔄 Güncelleme

### Docker Image:
```bash
# En son sürümü çek
docker pull ghcr.io/yourusername/image_processing:latest

# Container'ı yeniden başlat
docker-compose pull && docker-compose up -d
```

### Python Package:
```bash
# Package'i güncelle
pip install --upgrade face-recognition-system
```

## 📞 Destek

- 🐛 **Issues:** [GitHub Issues](https://github.com/yourusername/image_processing/issues)
- 📖 **Docs:** [Wiki](https://github.com/yourusername/image_processing/wiki)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/yourusername/image_processing/discussions)

## 📄 Lisans

MIT License - Detaylar için [LICENSE](LICENSE) dosyasına bakın.

---

**Made with ❤️ by Ahmed Taner** 