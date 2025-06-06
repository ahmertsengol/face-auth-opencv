# 🚀 **Installation Guide - Yeni PC'de Kurulum**

Bu rehber, **Optimize Face Recognition System**'i sıfırdan yeni bir bilgisayarda kurmak için hazırlanmıştır.

## 📋 **Sistem Gereksinimleri**

### **Minimum Gereksinimler:**
- **OS**: macOS 10.15+, Ubuntu 18.04+, Windows 10+
- **Python**: 3.10 veya üzeri
- **RAM**: 4GB (8GB önerilen)
- **Disk**: 2GB boş alan
- **Kamera**: USB webcam veya built-in kamera

### **macOS Özel Gereksinimler:**
```bash
# Homebrew yükle (yoksa)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# CMake yükle
brew install cmake
```

### **Ubuntu/Linux Özel Gereksinimler:**
```bash
# Sistem paketlerini güncelle
sudo apt update

# Python ve gerekli kütüphaneler
sudo apt install python3 python3-pip python3-venv
sudo apt install cmake build-essential
sudo apt install libgtk-3-dev libavcodec-dev libavformat-dev libswscale-dev
```

## 📦 **Adım 1: Projeyi İndir**

### **Git ile İndir (Önerilen):**
```bash
# Projeyi klonla
git clone https://github.com/ahmertsengol/face-auth-opencv.git
cd face-auth-opencv

# Son release'e geç
git checkout v2.0.0
```

### **ZIP ile İndir:**
```bash
# GitHub'dan ZIP indir ve çıkart
wget https://github.com/ahmertsengol/face-auth-opencv/archive/v2.0.0.zip
unzip v2.0.0.zip
cd face-auth-opencv-2.0.0
```

## ⚙️ **Adım 2: Otomatik Kurulum**

### **Tek Komutla Kurulum:**
```bash
# Sistemi kur ve test et
make install
make test
```

Bu komut şunları yapar:
- ✅ Python virtual environment oluşturur
- ✅ Tüm dependency'leri yükler
- ✅ Konfigürasyon dosyalarını oluşturur
- ✅ Veri dizinlerini hazırlar
- ✅ Sistem testlerini çalıştırır

## 🔍 **Adım 3: Kurulum Kontrolü**

```bash
# Sistem durumunu kontrol et
make status
```

**Beklenen Çıktı:**
```
📊 Sistem Durumu
==================
✅ Sanal ortam: Hazır
  Python 3.11.9
✅ Konfigürasyon: Hazır
  Dosya: config/app_config.json
✅ Veri dizini: Hazır
  Kullanıcı sayısı: 0
✅ Log dizini: Hazır
```

## 🎯 **Adım 4: İlk Kullanım**

### **4.1 İlk Kullanıcıyı Kaydet:**
```bash
make register
# İsim: Ahmet (enter)
# Kamera açılır → 's' ile 5 fotoğraf çek → 'q' ile çık
```

### **4.2 Yüz Tanımayı Test Et:**
```bash
make recognize
# Kamera açılır → Yüzünü göster → Tanıma sonucu
```

### **4.3 Sistem Performansını Test Et:**
```bash
make benchmark
# Performance: ~1.3ms/frame
# FPS: 15-30
# Memory: Optimal
```

## 🛠️ **Manuel Kurulum (Sorun Çıkarsa)**

### **5.1 Virtual Environment Oluştur:**
```bash
python3 -m venv venv_face_recognition
source venv_face_recognition/bin/activate  # macOS/Linux
# venv_face_recognition\Scripts\activate  # Windows
```

### **5.2 Dependencies Yükle:**
```bash
pip install --upgrade pip
pip install -r config/requirements.txt
```

### **5.3 Konfigürasyon Oluştur:**
```bash
python -c "
from config.app_config import get_config_manager
config_manager = get_config_manager()
config_manager.save_config()
print('✅ Konfigürasyon oluşturuldu')
"
```

### **5.4 Test Et:**
```bash
python main.py --help
```

## 📱 **Kamera Ayarları**

### **macOS:**
```bash
# Kamera izni ver
# System Preferences → Security & Privacy → Camera → Terminal/Python
```

### **Linux:**
```bash
# Kullanıcıyı video grubuna ekle
sudo usermod -a -G video $USER
# Oturumu yeniden başlat
```

### **Windows:**
```bash
# Windows Defender → Camera privacy settings → Allow apps
```

## 🚨 **Sorun Giderme**

### **Kamera Açılmıyor:**
```bash
# Kamera testi
python -c "
import cv2
cap = cv2.VideoCapture(0)
if cap.isOpened():
    print('✅ Kamera çalışıyor')
else:
    print('❌ Kamera sorunu')
cap.release()
"
```

### **Import Hataları:**
```bash
# Dependencies kontrol
pip list | grep -E "(opencv|numpy|dlib)"

# Eksikse yeniden yükle
pip install opencv-python==4.8.1.78
```

### **CMake Hataları (macOS):**
```bash
brew install cmake
pip uninstall dlib
pip install dlib
```

### **Memory Hataları:**
```bash
# Cache temizle
make optimize

# Konfigürasyonu resetle
python -c "
from config.app_config import get_config_manager
get_config_manager().reset_to_default()
"
```

## 📊 **Kurulum Sonrası Komutlar**

| Komut | Açıklama |
|-------|----------|
| `make status` | Sistem durumu |
| `make register` | Kullanıcı kaydet |
| `make recognize` | Yüz tanıma başlat |
| `make list` | Kullanıcıları listele |
| `make test` | Sistem testleri |
| `make benchmark` | Performance testi |
| `make backup` | Veri yedekle |
| `make help` | Tüm komutlar |

## 🎉 **Başarılı Kurulum Kontrolü**

Kurulum başarılıysa şu komutlar çalışmalı:

```bash
# 1. Sistem durumu ✅
make status

# 2. Test suite ✅ (8/8 passed)
make test  

# 3. Benchmark ✅ (~1.3ms/frame)
make benchmark

# 4. Kullanıcı kaydı ✅
make register

# 5. Yüz tanıma ✅
make recognize
```

## 📞 **Destek**

Sorun yaşarsan:
1. `make status` çalıştır
2. `make test` sonuçlarını kontrol et
3. `logs/app.log` dosyasını incele
4. GitHub Issues'da yeni ticket aç

**🚀 Kurulum tamamlandı! Face Recognition System kullanıma hazır!** 