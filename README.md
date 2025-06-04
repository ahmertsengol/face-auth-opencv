# 👤 Yüz Tanıma Sistemi

OpenCV ve Python kullanarak geliştirilmiş basit ama etkili bir yüz tanıma sistemi.

## 🚀 Özellikler

- ✅ Yeni kullanıcı kaydı (yüz verilerini kaydetme)
- ✅ Gerçek zamanlı yüz tanıma
- ✅ Çoklu kullanıcı desteği
- ✅ Clean Architecture tasarımı
- ✅ SOLID prensipleri uygulaması

## 📦 Kurulum

```bash
# Gerekli paketleri yükle
pip install -r requirements.txt

# Proje dizinini oluştur
mkdir -p data/users
```

## 🎯 Kullanım

### 1. Yeni Kullanıcı Kaydetme
```bash
python main.py register --name "Ahmet"
```

### 2. Yüz Tanıma Başlatma
```bash
python main.py recognize
```

### 3. Tüm Kullanıcıları Listeleme
```bash
python main.py list-users
```

## 📁 Proje Yapısı

```
image_processing/
├── core/
│   ├── __init__.py
│   ├── face_detector.py      # Yüz algılama servisi
│   ├── face_recognizer.py    # Yüz tanıma servisi
│   └── user_manager.py       # Kullanıcı yönetimi
├── data/
│   └── users/               # Kullanıcı yüz verileri
├── utils/
│   ├── __init__.py
│   ├── camera.py           # Kamera yönetimi
│   └── file_manager.py     # Dosya işlemleri
├── main.py                 # Ana uygulama
├── requirements.txt
└── README.md
```

## 🎮 Kontroller

- `q` - Çıkış
- `s` - Kayıt sırasında fotoğraf çekme
- `ESC` - Uygulama kapatma

## 🛠️ Teknolojiler

- Python 3.10+
- OpenCV
- Face Recognition
- NumPy
- Click (CLI interface) 