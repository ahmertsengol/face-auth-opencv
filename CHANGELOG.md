# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2024-12-19 - Project Restructure

### Added
- 📁 **Project restructuring** for better organization
- 🏗️ **Makefile** for easy project management
- 📄 **.gitignore** comprehensive ignore rules
- 📋 **CHANGELOG.md** for tracking changes
- 🗂️ **scripts/** directory for setup and test files
- ⚙️ **config/** directory for configuration files

### Changed
- 📦 Moved `setup_venv.py` to `scripts/setup_venv.py`
- 🧪 Moved `test_system.py` to `scripts/test_system.py`
- 🚀 Moved `activate_project.sh` to `scripts/activate_project.sh`
- 📝 Moved `requirements_venv.txt` to `config/requirements.txt`
- 📖 Updated README.md with new structure and comprehensive documentation

### Removed
- ❌ Deleted unused `setup.py` (replaced by setup_venv.py)
- ❌ Deleted problematic `requirements.txt` (cmake issues)
- ❌ Deleted redundant `requirements_simple.txt`
- ❌ Deleted redundant `install_macos.py` (merged into setup_venv.py)
- ❌ Removed `test_data/` directory (test artifacts)

### New Commands
- `make install` - Complete setup with virtual environment
- `make test` - Run system tests
- `make register` - Interactive user registration
- `make recognize` - Start face recognition
- `make list` - List registered users
- `make clean` - Clean temporary files
- `make clean-venv` - Remove virtual environment
- `make help` - Show all available commands

## [1.0.0] - 2024-12-19

### Added
- 🎯 Clean Architecture ve SOLID prensipleriyle yüz tanıma sistemi
- 👤 Kullanıcı kayıt sistemi (çoklu fotoğraf desteği)
- 👁️ Gerçek zamanlı yüz tanıma
- 🐍 Sanal ortam destekli kurulum
- 📦 macOS için cmake problemi çözümlü setup
- 🧪 Kapsamlı test sistemi
- 📋 CLI arayüz (Click framework)
- 💾 JSON tabanlı veri persistance
- 🔄 Hibrit yüz algılama (OpenCV + dlib)

### Project Structure
- `core/` - İş mantığı katmanı
- `utils/` - Altyapı katmanı  
- `scripts/` - Kurulum ve test scriptleri
- `config/` - Yapılandırma dosyaları
- `docs/` - Dokümantasyon
- `data/` - Kullanıcı verileri
- `logs/` - Sistem logları

### Components
- **FaceDetector**: Yüz algılama servisi
- **FaceRecognizer**: Yüz tanıma servisi
- **UserManager**: Kullanıcı veri yönetimi
- **CameraManager**: Kamera kontrol sistemi
- **FileManager**: Dosya işlemleri

### Commands
- `make install` - Tam kurulum
- `make test` - Sistem testi
- `make register` - Kullanıcı kayıt
- `make recognize` - Yüz tanıma
- `make list` - Kullanıcı listesi

### Technical Details
- Python 3.8+ desteği
- Type hints kullanımı
- Exception handling
- Context managers
- Dataclass kullanımı
- Modern Python practices 