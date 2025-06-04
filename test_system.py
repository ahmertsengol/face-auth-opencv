#!/usr/bin/env python3
"""
Sistem testi dosyası - Bileşenlerin çalışıp çalışmadığını kontrol eder
"""

import sys
import traceback
from datetime import datetime
import numpy as np

def test_imports():
    """Gerekli modüllerin import edilip edilemediğini test eder."""
    print("📦 Import testleri...")
    
    try:
        import cv2
        print(f"✅ OpenCV: {cv2.__version__}")
    except ImportError as e:
        print(f"❌ OpenCV import hatası: {e}")
        return False
    
    try:
        import face_recognition
        print("✅ Face Recognition: OK")
    except ImportError as e:
        print(f"❌ Face Recognition import hatası: {e}")
        return False
    
    try:
        import numpy as np
        print(f"✅ NumPy: {np.__version__}")
    except ImportError as e:
        print(f"❌ NumPy import hatası: {e}")
        return False
    
    try:
        import click
        print(f"✅ Click: {click.__version__}")
    except ImportError as e:
        print(f"❌ Click import hatası: {e}")
        return False
    
    return True


def test_core_modules():
    """Core modüllerini test eder."""
    print("\n🧩 Core modül testleri...")
    
    try:
        from core import FaceDetector, FaceRecognizer, UserManager
        print("✅ Core modülleri import edildi")
    except ImportError as e:
        print(f"❌ Core modül import hatası: {e}")
        return False
    
    try:
        # FaceDetector testi
        detector = FaceDetector()
        print("✅ FaceDetector oluşturuldu")
    except Exception as e:
        print(f"❌ FaceDetector hatası: {e}")
        return False
    
    try:
        # FaceRecognizer testi
        recognizer = FaceRecognizer()
        print("✅ FaceRecognizer oluşturuldu")
    except Exception as e:
        print(f"❌ FaceRecognizer hatası: {e}")
        return False
    
    try:
        # UserManager testi
        user_manager = UserManager()
        print("✅ UserManager oluşturuldu")
    except Exception as e:
        print(f"❌ UserManager hatası: {e}")
        return False
    
    return True


def test_utils_modules():
    """Utils modüllerini test eder."""
    print("\n🛠️ Utils modül testleri...")
    
    try:
        from utils import CameraManager, FileManager
        print("✅ Utils modülleri import edildi")
    except ImportError as e:
        print(f"❌ Utils modül import hatası: {e}")
        return False
    
    try:
        # FileManager testi
        if FileManager.ensure_directory("test_temp"):
            print("✅ FileManager çalışıyor")
            FileManager.delete_directory("test_temp")
        else:
            print("❌ FileManager test başarısız")
            return False
    except Exception as e:
        print(f"❌ FileManager hatası: {e}")
        return False
    
    return True


def test_camera_availability():
    """Kamera erişimini test eder."""
    print("\n📷 Kamera erişim testi...")
    
    try:
        from utils import CameraManager
        camera = CameraManager()
        
        if camera.test_camera():
            print("✅ Kamera erişimi başarılı")
            camera.release()
            return True
        else:
            print("⚠️  Kamera erişilemiyor (normal olabilir)")
            camera.release()
            return True  # Kamera yoksa da normal kabul et
    except Exception as e:
        print(f"❌ Kamera test hatası: {e}")
        return False


def test_face_detection():
    """Yüz algılama fonksiyonlarını test eder."""
    print("\n🤖 Yüz algılama testi...")
    
    try:
        from core import FaceDetector
        import numpy as np
        
        detector = FaceDetector()
        
        # Dummy test görüntüsü oluştur
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # OpenCV yüz algılama testi
        faces = detector.detect_faces_opencv(test_image)
        print(f"✅ OpenCV yüz algılama çalışıyor (test sonuç: {len(faces)} yüz)")
        
        # Face encodings testi
        encodings = detector.get_face_encodings(test_image)
        print(f"✅ Face encodings çalışıyor (test sonuç: {len(encodings)} encoding)")
        
        return True
        
    except Exception as e:
        print(f"❌ Yüz algılama test hatası: {e}")
        traceback.print_exc()
        return False


def test_data_persistence():
    """Veri kaydetme/yükleme işlemlerini test eder."""
    print("\n💾 Veri persistence testi...")
    
    try:
        from core.user_manager import UserManager, UserData
        import numpy as np
        
        user_manager = UserManager("test_data")
        
        # Test verisi oluştur
        test_user = UserData(
            name="Test User",
            face_encodings=[np.random.random(128) for _ in range(2)],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        # Kaydet
        if user_manager.save_user(test_user):
            print("✅ Kullanıcı kaydedildi")
        else:
            print("❌ Kullanıcı kaydedilemedi")
            return False
        
        # Yükle
        loaded_user = user_manager.load_user("Test User")
        if loaded_user and loaded_user.name == "Test User":
            print("✅ Kullanıcı yüklendi")
        else:
            print("❌ Kullanıcı yüklenemedi")
            return False
        
        # Temizle
        user_manager.delete_user("Test User")
        FileManager.delete_directory("test_data")
        print("✅ Test verileri temizlendi")
        
        return True
        
    except Exception as e:
        print(f"❌ Veri persistence test hatası: {e}")
        traceback.print_exc()
        return False


def main():
    """Ana test fonksiyonu."""
    print("🧪 Yüz Tanıma Sistemi - Bileşen Testleri")
    print("=" * 50)
    
    tests = [
        ("Import Testleri", test_imports),
        ("Core Modül Testleri", test_core_modules),
        ("Utils Modül Testleri", test_utils_modules),
        ("Kamera Erişim Testi", test_camera_availability),
        ("Yüz Algılama Testi", test_face_detection),
        ("Veri Persistence Testi", test_data_persistence),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test hatası: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Sonuçları:")
    print(f"✅ Başarılı: {passed}")
    print(f"❌ Başarısız: {failed}")
    print(f"📈 Başarı oranı: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 Tüm testler başarıyla geçti! Sistem kullanıma hazır.")
        return 0
    else:
        print(f"\n⚠️  {failed} test başarısız. Lütfen hataları kontrol edin.")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n👋 Test iptal edildi.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Beklenmeyen hata: {e}")
        traceback.print_exc()
        sys.exit(1) 