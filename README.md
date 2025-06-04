# 👤 Yüz Tanıma Sistemi

Clean Architecture ve SOLID prensipleriyle geliştirilmiş, OpenCV ve Python tabanlı profesyonel yüz tanıma sistemi.

## 🚀 Özellikler

- ✅ **Yüz Algılama**: Hibrit yaklaşım (OpenCV + dlib)
- ✅ **Gerçek Zamanlı Tanıma**: Anlık yüz tanıma sistemi
- ✅ **Çoklu Kullanıcı**: Sınırsız kullanıcı kayıt desteği
- ✅ **Sanal Ortam**: İzole edilmiş Python ortamı
- ✅ **macOS Desteği**: cmake problemleri çözümü dahil
- ✅ **Clean Architecture**: SOLID prensipleri uygulaması
- ✅ **Modern CLI**: Click framework ile kullanıcı dostu arayüz
- ✅ **Kapsamlı Testler**: Otomatik sistem doğrulama

## 📦 Hızlı Kurulum

```bash
# 1. Projeyi klonlayın
git clone <repository-url>
cd image_processing

# 2. Tek komutla kur
make install

# 3. Test edin
make test
```

## 🎯 Kullanım

### Temel Komutlar

```bash
# Sanal ortamı aktifleştir
source venv_face_recognition/bin/activate
# veya
./scripts/activate_project.sh

# Kullanıcı kaydet
make register
# veya
python main.py register -n "Ahmet"

# Yüz tanıma başlat
make recognize
# veya  
python main.py recognize

# Kullanıcıları listele
make list
```

### Makefile Komutları

```bash
make help           # Tüm komutları göster
make install        # Projeyi kur
make test          # Sistem testi
make register      # Kullanıcı kaydet (interaktif)
make recognize     # Yüz tanıma başlat
make list          # Kullanıcıları listele
make clean         # Geçici dosyaları temizle
make clean-venv    # Sanal ortamı sil
```

## 📁 Proje Yapısı

```
image_processing/
├── 📂 core/                    # İş Mantığı Katmanı
│   ├── __init__.py
│   ├── face_detector.py        # Yüz algılama servisi
│   ├── face_recognizer.py      # Yüz tanıma servisi
│   └── user_manager.py         # Kullanıcı veri yönetimi
├── 📂 utils/                   # Altyapı Katmanı
│   ├── __init__.py
│   ├── camera.py              # Kamera yönetimi
│   └── file_manager.py        # Dosya işlemleri
├── 📂 scripts/                 # Kurulum & Test
│   ├── setup_venv.py          # Sanal ortam kurulumu
│   ├── test_system.py         # Sistem testleri
│   └── activate_project.sh    # Ortam aktivasyonu
├── 📂 config/                  # Yapılandırma
│   └── requirements.txt       # Python paketleri
├── 📂 data/                    # Veri Katmanı
│   ├── users/                 # Kullanıcı yüz verileri
│   └── backups/               # Yedek dosyaları
├── 📂 logs/                    # Sistem Logları
├── 📄 main.py                  # Ana Uygulama
├── 📄 Makefile                 # Proje komutları
├── 📄 README.md               # Bu dosya
├── 📄 CHANGELOG.md            # Değişiklik günlüğü
└── 📄 .gitignore              # Git ignore kuralları
```

## 🏗️ Mimari

### Clean Architecture Katmanları

1. **Core (İş Mantığı)**
   - `FaceDetector`: Yüz algılama algoritmaları
   - `FaceRecognizer`: Yüz tanıma ve eşleştirme
   - `UserManager`: Kullanıcı veri modeli

2. **Utils (Altyapı)**
   - `CameraManager`: Kamera erişim kontrolü
   - `FileManager`: Dosya sistem işlemleri

3. **Presentation (Sunum)**
   - `main.py`: CLI arayüzü ve komutlar
   - Click framework tabanlı kullanıcı etkileşimi

### SOLID Prensipleri

- **S** - Single Responsibility: Her sınıf tek işten sorumlu
- **O** - Open/Closed: Genişletilmeye açık, değişime kapalı
- **L** - Liskov Substitution: Alt sınıflar üst sınıfları değiştirebilir
- **I** - Interface Segregation: Küçük ve özel arayüzler
- **D** - Dependency Inversion: Abstraksiyon bağımlılığı

## 🛠️ Gereksinimler

- **Python**: 3.8+
- **İşletim Sistemi**: macOS, Linux, Windows
- **Kamera**: USB/built-in webcam
- **Bellek**: 4GB+ RAM önerilir

### Sistem Bağımlılıkları

**macOS:**
```bash
brew install cmake
```

**Ubuntu/Debian:**
```bash
sudo apt-get install cmake python3-dev
```

**Windows:**
```bash
# Visual Studio Build Tools veya cmake tools
```

## 🎮 Kontroller

### Kullanıcı Kayıt Modu
- `s` - Fotoğraf çek
- `q` - Çıkış
- `ESC` - İptal

### Yüz Tanıma Modu
- `q` - Yüz tanımayı durdur
- `ESC` - Uygulamayı kapat

## 🧪 Test

```bash
# Tam sistem testi
make test

# Manuel test
python scripts/test_system.py

# Bileşen testleri
python -m pytest tests/  # (opsiyonel)
```

## 🚨 Sorun Giderme

### cmake Hatası (macOS)
```bash
brew install cmake
make clean-venv
make install
```

### Kamera Erişim Hatası
```bash
# macOS: System Preferences > Security & Privacy > Camera
# Linux: Kullanıcıyı video grubuna ekle
sudo usermod -a -G video $USER
```

### Paket Kurulamıyor
```bash
# Sanal ortamı sıfırla
make clean-venv
make install
```

## 🤝 Geliştirme

```bash
# Geliştirme araçlarını kur
make dev-install

# Kodu formatla
make format

# Kod kalitesi kontrolü
make lint
```

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🙏 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📧 İletişim

Sorularınız için issue açabilirsiniz.

---

> 🎯 **Clean Architecture** + **SOLID Principles** + **Modern Python** = **Professional Face Recognition System** 