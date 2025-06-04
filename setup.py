#!/usr/bin/env python3
"""
Kurulum script'i - Sistem kurulumu ve hazırlık
"""

import os
import sys
import subprocess
from pathlib import Path


def install_requirements():
    """Gerekli paketleri yükler."""
    print("📦 Gerekli paketler yükleniyor...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Paketler başarıyla yüklendi!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Paket yükleme hatası: {e}")
        return False


def create_directories():
    """Gerekli dizinleri oluşturur."""
    print("📁 Dizinler oluşturuluyor...")
    
    directories = [
        "data",
        "data/users",
        "data/backups",
        "logs"
    ]
    
    for directory in directories:
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"✅ {directory} dizini hazır")
        except Exception as e:
            print(f"❌ {directory} dizini oluşturulamadı: {e}")
            return False
    
    return True


def check_system():
    """Sistem gereksinimlerini kontrol eder."""
    print("🔍 Sistem kontrolleri...")
    
    # Python versiyonu kontrolü
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ gerekli!")
        return False
    else:
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} uygun")
    
    # Platform kontrolü
    platform = sys.platform
    print(f"✅ Platform: {platform}")
    
    return True


def run_tests():
    """Sistem testlerini çalıştırır."""
    print("🧪 Sistem testleri çalıştırılıyor...")
    
    try:
        result = subprocess.run([sys.executable, "test_system.py"], 
                              capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("Stderr:", result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Test çalıştırma hatası: {e}")
        return False


def main():
    """Ana kurulum fonksiyonu."""
    print("🚀 Yüz Tanıma Sistemi Kurulumu")
    print("=" * 50)
    
    steps = [
        ("Sistem Kontrolü", check_system),
        ("Dizin Oluşturma", create_directories),
        ("Paket Yükleme", install_requirements),
        ("Sistem Testleri", run_tests),
    ]
    
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        if not step_func():
            print(f"❌ {step_name} başarısız!")
            return False
        print(f"✅ {step_name} tamamlandı!")
    
    print("\n" + "=" * 50)
    print("🎉 Kurulum başarıyla tamamlandı!")
    print("\n📖 Kullanım:")
    print("  python main.py --help          # Yardım")
    print("  python main.py test            # Sistem testi")
    print("  python main.py register -n Ahmet  # Kullanıcı kayıt")
    print("  python main.py recognize       # Yüz tanıma")
    print("  python main.py list-users      # Kullanıcı listesi")
    
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
    except Exception as e:
        print(f"❌ Kurulum hatası: {e}")
        sys.exit(1) 