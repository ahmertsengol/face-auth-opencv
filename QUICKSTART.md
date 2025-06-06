# ⚡ **Quick Start - 5 Dakikada Başla**

Sadece **3 komut** ile face recognition sistemi çalıştır!

## 🚀 **Hızlı Kurulum**

```bash
# 1. Projeyi klonla
git clone https://github.com/ahmertsengol/face-auth-opencv.git
cd face-auth-opencv

# 2. Sistemi kur (2-3 dakika)
make install

# 3. Test et
make status
```

## 👤 **İlk Kullanım (2 dakika)**

```bash
# Kullanıcı kaydet
make register
# → İsminizi yazın
# → Kameraya bakın  
# → 's' tuşu ile 5 fotoğraf çekin

# Yüz tanımayı başlat
make recognize
# → Kameraya bakın
# → Otomatik tanıma başlar!
```

## 🎮 **Temel Komutlar**

| Ne Yapmak İstiyorsun? | Komut |
|----------------------|-------|
| Kullanıcı ekle | `make register` |
| Yüz tanıma başlat | `make recognize` |
| Kimler kayıtlı? | `make list` |
| Sistem durumu? | `make status` |
| Birini sil | `make delete USER=isim` |

## 🚨 **Sorun mu var?**

```bash
# Sistem kontrolü
make status

# Test çalıştır
make test

# Yardım al
make help
```

## 🎯 **Önemli Tuşlar**

- **'s'** → Fotoğraf çek (kayıt sırasında)
- **'q'** → Çık/Durdur

**🎉 Bu kadar! 5 dakikada hazır!** 