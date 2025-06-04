#!/usr/bin/env python3
"""
Sanal Ortam ile Yüz Tanıma Sistemi Kurulumu
macOS için cmake problemi çözümlü sanal ortam kurulumu
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description="", check=True):
    """Komutu çalıştırır ve sonucunu kontrol eder."""
    print(f"🔄 {description or command}")
    try:
        result = subprocess.run(command, shell=True, check=check, 
                              capture_output=True, text=True)
        if result.stdout:
            print(f"✅ {description or command}")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Hata: {description or command}")
        if e.stdout:
            print(f"   Stdout: {e.stdout}")
        if e.stderr:
            print(f"   Stderr: {e.stderr}")
        return False


def check_venv_active():
    """Sanal ortamın aktif olduğunu kontrol eder."""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)


def main():
    print("🐍 Sanal Ortam ile Yüz Tanıma Sistemi Kurulumu")
    print("=" * 60)
    
    # Sanal ortam kontrolü
    if not check_venv_active():
        print("⚠️  Sanal ortam aktif değil!")
        print("\nÖnce şu komutları çalıştırın:")
        print("  python3 -m venv venv_face_recognition")
        print("  source venv_face_recognition/bin/activate")
        print("  python scripts/setup_venv.py")
        return False
    
    print("✅ Sanal ortam aktif!")
    print(f"🐍 Python Path: {sys.executable}")
    
    # 1. Pip güncellemesi
    print("\n1️⃣ Pip Güncellemesi")
    run_command("pip install --upgrade pip", "pip güncelleniyor")
    
    # 2. Sistem bağımlılıkları (macOS)
    print("\n2️⃣ Sistem Bağımlılıkları (macOS)")
    
    # Homebrew kontrolü
    if not run_command("which brew", "Homebrew kontrol", check=False):
        print("⚠️  Homebrew bulunamadı. Manuel kurulum gerekebilir:")
        print("   /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
    else:
        # cmake kurulumu
        if not run_command("cmake --version", "cmake kontrol", check=False):
            run_command("brew install cmake", "cmake kuruluyor")
    
    # 3. Temel paketler
    print("\n3️⃣ Temel Python Paketleri")
    basic_packages = [
        "wheel",
        "setuptools", 
        "numpy",
        "opencv-python",
        "pillow",
        "click",
        "python-dotenv"
    ]
    
    for package in basic_packages:
        run_command(f"pip install {package}", f"{package} kuruluyor", check=False)
    
    # 4. dlib ve face-recognition (özel yaklaşım)
    print("\n4️⃣ face-recognition Kurulumu")
    
    # Alternatif 1: Direkt pip ile
    if run_command("pip install dlib", "dlib kuruluyor", check=False):
        run_command("pip install face-recognition", "face-recognition kuruluyor", check=False)
    else:
        print("⚠️  dlib pip ile kurulamadı. Alternatif yöntemler deneniyor...")
        
        # Alternatif 2: conda forge ile (conda varsa)
        if run_command("which conda", "conda kontrol", check=False):
            run_command("conda install -c conda-forge dlib", "conda ile dlib", check=False)
            run_command("pip install face-recognition", "face-recognition kuruluyor", check=False)
        else:
            print("💡 Manuel çözüm:")
            print("   1. brew install cmake")
            print("   2. pip install dlib")
            print("   3. pip install face-recognition")
    
    # 5. Proje dizinleri
    print("\n5️⃣ Proje Dizinleri")
    directories = ["data", "data/users", "data/backups", "logs"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ {directory} dizini hazır")
    
    # 6. Aktivasyon scripti güncelle
    print("\n6️⃣ Aktivasyon Scripti")
    activation_script = """#!/bin/bash
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
"""
    
    with open("scripts/activate_project.sh", "w") as f:
        f.write(activation_script)
    
    # Çalıştırılabilir yap
    os.chmod("scripts/activate_project.sh", 0o755)
    print("✅ scripts/activate_project.sh güncellendi")
    
    # 7. Test
    print("\n7️⃣ Sistem Testi")
    if run_command("python scripts/test_system.py", "Sistem testleri çalıştırılıyor", check=False):
        print("\n🎉 Sanal ortam kurulumu başarıyla tamamlandı!")
    else:
        print("⚠️  Bazı testler başarısız, ama temel sistem çalışabilir")
    
    print("\n" + "=" * 60)
    print("📖 Kullanım Rehberi:")
    print("  # Makefile komutları (önerilen):")
    print("  make help              # Yardım")
    print("  make register          # Kullanıcı kaydet")
    print("  make recognize         # Yüz tanıma")
    print("  make list              # Kullanıcı listesi")
    print("")
    print("  # Manuel sanal ortam:")
    print("  source venv_face_recognition/bin/activate")
    print("  ./scripts/activate_project.sh")
    print("")
    print("  # Sanal ortamdan çık:")
    print("  deactivate")
    
    return True


if __name__ == "__main__":
    try:
        if main():
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Kurulum iptal edildi.")
        sys.exit(1) 