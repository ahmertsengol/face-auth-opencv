#!/bin/bash
# Yüz Tanıma Sistemi - Sanal Ortam Aktivasyonu

echo "🐍 Yüz Tanıma Sistemi Sanal Ortamı Aktifleştiriliyor..."
source venv_face_recognition/bin/activate

echo "✅ Sanal ortam aktif!"
echo "🚀 Kullanılabilir komutlar:"
echo "  make help              # Tüm komutları göster"
echo "  make register          # Kullanıcı kaydet"
echo "  make recognize         # Yüz tanıma başlat"
echo "  make list              # Kullanıcıları listele"
echo "  make test              # Sistem testi"
echo ""
echo "❌ Çıkmak için: deactivate"
