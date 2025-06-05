# 👤 Face Authentication System

Python ve OpenCV ile geliştirilmiş basit yüz tanıma sistemi.

## 🚀 Özellikler

- ✅ Kullanıcı kaydı (yüz verisi)
- ✅ Gerçek zamanlı yüz tanıma
- ✅ Çoklu kullanıcı desteği
- ✅ Sanal ortam desteği

## 📦 Kurulum

```bash
# Projeyi klonla
git clone https://github.com/ahmertsengol/face-auth-opencv.git
cd face-auth-opencv

# Tek komutla kur
make install

# Test et
make test
```

## 🎯 Kullanım

### Temel Komutlar

```bash
# Kullanıcı kaydet
make register

# Yüz tanıma başlat
make recognize

# Kullanıcıları listele
make list
```

### Manuel Komutlar

```bash
# Sanal ortamı aktifleştir
source venv_face_recognition/bin/activate

# Kullanıcı kaydet
python main.py register -n "İsim"

# Yüz tanıma
python main.py recognize

# Kullanıcı listesi
python main.py list-users
```

## 🎮 Kontroller

**Kayıt Sırasında:**
- `s` - Fotoğraf çek
- `q` - Çıkış

**Tanıma Sırasında:**
- `q` - Yüz tanımayı durdur

## 🛠️ Gereksinimler

- Python 3.8+
- Webcam/USB kamera
- macOS: `brew install cmake`

## 📁 Proje Yapısı

```
face-auth-opencv/
├── core/           # Yüz tanıma algoritmaları
├── utils/          # Kamera ve dosya yönetimi
├── scripts/        # Kurulum araçları
├── config/         # Ayar dosyaları
├── data/           # Kullanıcı verileri
└── main.py         # Ana uygulama
```

## 🚨 Sorun Giderme

**macOS cmake hatası:**
```bash
brew install cmake
make clean-venv
make install
```

**Kamera erişim hatası:**
- macOS: System Preferences > Security & Privacy > Camera

## 📄 Lisans

MIT License 