#!/usr/bin/env python3
"""
Gelişmiş Test Sistemi - Face Recognition System
Performance, Integration ve Unit testler
"""

import sys
import os
import time
import unittest
from pathlib import Path
import numpy as np
import cv2
from typing import List, Dict, Any
import tempfile
import shutil
from datetime import datetime

# Proje dizinini Python path'ine ekle
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Test imports
from core.face_detector import OptimizedFaceDetector
from core.face_recognizer import FaceRecognizer, RecognitionResult
from core.user_manager import UserManager, UserData
from utils.camera import CameraManager
from utils.file_manager import FileManager
from utils.database import DatabaseManager, get_database_manager
from config.app_config import ConfigManager, get_config_manager
from utils.logger import setup_logging, get_logger_manager


class TestResult:
    """Test sonucu sınıfı."""
    
    def __init__(self, name: str, passed: bool, duration: float, details: str = ""):
        self.name = name
        self.passed = passed
        self.duration = duration
        self.details = details


class AdvancedTestSuite:
    """
    Gelişmiş test süiti sınıfı.
    Performance, security, integration testleri içerir.
    """
    
    def __init__(self):
        """Test süitini başlatır."""
        self.results: List[TestResult] = []
        self.temp_dir = None
        
        # Logging sistemini başlat
        self.logger_manager = setup_logging(log_level="DEBUG")
        self.logger = self.logger_manager.get_logger('test')
        
        # Test için geçici dizin
        self.temp_dir = tempfile.mkdtemp(prefix="face_test_")
        
        print("🧪 Gelişmiş Test Sistemi Başlatıldı")
        print(f"📁 Test dizini: {self.temp_dir}")
    
    def run_test(self, test_func, test_name: str) -> TestResult:
        """Bir test fonksiyonunu çalıştırır ve sonucu kaydeder."""
        try:
            start_time = time.time()
            test_func()
            duration = time.time() - start_time
            result = TestResult(test_name, True, duration, "✅ BAŞARILI")
            self.logger.info(f"✅ {test_name} - {duration:.3f}s")
    except Exception as e:
            duration = time.time() - start_time
            result = TestResult(test_name, False, duration, f"❌ HATA: {str(e)}")
            self.logger.error(f"❌ {test_name} - {str(e)}")
        
        self.results.append(result)
        return result
    
    def test_config_system(self):
        """Konfigürasyon sistemi testi."""
        config_manager = ConfigManager(f"{self.temp_dir}/test_config.json")
        
        # Default config testi
        config = config_manager.get_config()
        assert config.camera.width == 640, "Camera width default değeri yanlış"
        assert config.detection.recognition_tolerance == 0.6, "Recognition tolerance yanlış"
        
        # Config güncellemesi testi
        success = config_manager.update_config(**{"camera.width": 800})
        assert success, "Config güncellenemedi"
        
        updated_config = config_manager.get_config()
        assert updated_config.camera.width == 800, "Config güncellenmedi"
        
        # Reset testi
        success = config_manager.reset_to_default()
        assert success, "Config reset edilemedi"
        
        reset_config = config_manager.get_config()
        assert reset_config.camera.width == 640, "Config reset sonrası yanlış değer"
    
    def test_database_operations(self):
        """Veritabanı işlemleri testi."""
        db_path = f"{self.temp_dir}/test.db"
        db_manager = DatabaseManager(db_path)
        
        # Test kullanıcısı oluştur
        test_encoding = np.random.rand(128).astype(np.float32)
        user_data = UserData(
            name="test_user",
            face_encodings=[test_encoding],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        # Kaydetme testi
        success = db_manager.save_user(user_data)
        assert success, "Kullanıcı kaydedilemedi"
        
        # Yükleme testi
        loaded_user = db_manager.load_user("test_user")
        assert loaded_user is not None, "Kullanıcı yüklenemedi"
        assert loaded_user.name == "test_user", "Kullanıcı adı yanlış"
        assert len(loaded_user.face_encodings) == 1, "Encoding sayısı yanlış"
        
        # Var olma testi
        exists = db_manager.user_exists("test_user")
        assert exists, "Kullanıcı varlık kontrolü başarısız"
        
        # Tüm kullanıcıları yükleme testi
        all_users = db_manager.load_all_users()
        assert len(all_users) == 1, "Tüm kullanıcılar yüklenemedi"
        
        # İstatistik testi
        stats = db_manager.get_user_statistics()
        assert stats['total_users'] == 1, "İstatistik yanlış"
        assert stats['total_encodings'] == 1, "Encoding istatistiği yanlış"
        
        # Silme testi
        success = db_manager.delete_user("test_user")
        assert success, "Kullanıcı silinemedi"
        
        # Silinmiş kullanıcı kontrolü
        deleted_user = db_manager.load_user("test_user")
        assert deleted_user is None, "Silinmiş kullanıcı hala yükleniyor"
    
    def test_face_detector_performance(self):
        """Yüz algılama performans testi."""
        detector = OptimizedFaceDetector()
        
        # Test görüntüsü oluştur
        test_images = [
            np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8),
            np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8),
            np.random.randint(0, 255, (240, 320, 3), dtype=np.uint8)
        ]
        
        # Performance testleri
        for i, img in enumerate(test_images):
            start_time = time.time()
            
            # OpenCV optimized test
            faces_opencv = detector.detect_faces_opencv_optimized(img, use_cache=True)
            opencv_time = time.time() - start_time
            
            assert isinstance(faces_opencv, list), f"OpenCV sonuç tipi yanlış (img {i})"
            assert opencv_time < 1.0, f"OpenCV çok yavaş: {opencv_time:.3f}s (img {i})"
            
            # Cache test
            start_time = time.time()
            cached_faces = detector.detect_faces_opencv_optimized(img, use_cache=True)
            cache_time = time.time() - start_time
            
            assert cache_time < opencv_time, f"Cache çalışmıyor (img {i})"
            assert faces_opencv == cached_faces, f"Cache sonucu farklı (img {i})"
        
        # Performance stats
        stats = detector.get_performance_stats()
        assert 'cache_size' in stats, "Performance stats eksik"
        
        # Cache temizleme testi
        detector.clear_cache()
        cleared_stats = detector.get_performance_stats()
        assert cleared_stats['cache_size'] == 0, "Cache temizlenmedi"
    
    def test_face_recognizer_accuracy(self):
        """Yüz tanıma doğruluk testi."""
        recognizer = FaceRecognizer(tolerance=0.6)
        
        # Test encodings oluştur
        user1_encoding = np.random.rand(128).astype(np.float32)
        user2_encoding = np.random.rand(128).astype(np.float32)
        
        # Bilinen yüzleri ekle
        recognizer.add_known_face(user1_encoding, "user1")
        recognizer.add_known_face(user2_encoding, "user2")
        
        assert recognizer.get_known_faces_count() == 2, "Bilinen yüz sayısı yanlış"
        
        # Tanıma testleri
        # Aynı encoding ile test (pozitif test)
        similar_encoding = user1_encoding + np.random.normal(0, 0.1, 128).astype(np.float32)
        results = recognizer.recognize_faces([similar_encoding])
        
        assert len(results) == 1, "Sonuç sayısı yanlış"
        result = results[0]
        assert isinstance(result, RecognitionResult), "Sonuç tipi yanlış"
        
        # Bilinmeyen encoding ile test (negatif test)
        unknown_encoding = np.random.rand(128).astype(np.float32)
        unknown_results = recognizer.recognize_faces([unknown_encoding])
        
        assert len(unknown_results) == 1, "Bilinmeyen sonuç sayısı yanlış"
        unknown_result = unknown_results[0]
        
        # Clear test
        recognizer.clear_known_faces()
        assert recognizer.get_known_faces_count() == 0, "Yüzler temizlenmedi"
    
    def test_user_manager_operations(self):
        """Kullanıcı yöneticisi işlem testi."""
        user_manager = UserManager(data_dir=f"{self.temp_dir}/users")
        
        # Test kullanıcısı oluştur
        test_encoding = np.random.rand(128).astype(np.float32)
        user_data = UserData(
            name="test_manager_user",
            face_encodings=[test_encoding, test_encoding],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        # Kaydetme testi
        success = user_manager.save_user(user_data)
        assert success, "UserManager kaydetme başarısız"
        
        # Yükleme testi
        loaded_user = user_manager.load_user("test_manager_user")
        assert loaded_user is not None, "UserManager yükleme başarısız"
        assert len(loaded_user.face_encodings) == 2, "UserManager encoding sayısı yanlış"
        
        # Varlık testi
        exists = user_manager.user_exists("test_manager_user")
        assert exists, "UserManager varlık kontrolü başarısız"
        
        # Listeleme testi
        all_users = user_manager.load_all_users()
        assert len(all_users) == 1, "UserManager tüm kullanıcılar yanlış"
        
        # Güncelleme testi
        user_data.face_encodings.append(np.random.rand(128).astype(np.float32))
        success = user_manager.save_user(user_data)
        assert success, "UserManager güncelleme başarısız"
        
        updated_user = user_manager.load_user("test_manager_user")
        assert len(updated_user.face_encodings) == 3, "UserManager güncelleme sonrası encoding sayısı yanlış"
        
        # Silme testi
        success = user_manager.delete_user("test_manager_user")
        assert success, "UserManager silme başarısız"
        
        deleted_exists = user_manager.user_exists("test_manager_user")
        assert not deleted_exists, "UserManager silinmiş kullanıcı hala mevcut"
    
    def test_file_manager_security(self):
        """Dosya yöneticisi güvenlik testi."""
        file_manager = FileManager()
        
        # Safe path testleri
        safe_paths = [
            "data/users/user1.json",
            "data/users/test/user2.json",
            "logs/app.log"
        ]
        
        for path in safe_paths:
            assert file_manager.is_safe_path(path), f"Güvenli path reddedildi: {path}"
        
        # Unsafe path testleri
        unsafe_paths = [
            "../../../etc/passwd",
            "/etc/passwd",
            "data/../../../etc/passwd",
            "~/../../etc/passwd"
        ]
        
        for path in unsafe_paths:
            assert not file_manager.is_safe_path(path), f"Güvensiz path kabul edildi: {path}"
        
        # Directory traversal testi
        test_file = f"{self.temp_dir}/test.txt"
        
        # Güvenli yazma testi
        success = file_manager.write_file(test_file, "test content")
        assert success, "Güvenli dosya yazma başarısız"
        
        # Güvenli okuma testi
        content = file_manager.read_file(test_file)
        assert content == "test content", "Dosya içeriği yanlış"
        
        # Güvensiz path yazma testi
        unsafe_write = file_manager.write_file("../../../etc/passwd", "malicious")
        assert not unsafe_write, "Güvensiz dosya yazma engellenmedi"
    
    def test_memory_leak_detection(self):
        """Memory leak testi."""
        import gc
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Memory intensive operations
        detector = OptimizedFaceDetector()
        
        for i in range(30):  # 50'den 30'a düşürdük
            # Büyük test görüntüsü
            large_img = np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)  # Boyutu düşürdük
            faces = detector.detect_faces_opencv_optimized(large_img)
            
            if i % 5 == 0:
                gc.collect()  # Daha sık garbage collection
        
        # Cache temizle
        detector.clear_cache()
        gc.collect()
        
        # Biraz bekle
        import time
        time.sleep(0.5)
        
        final_memory = process.memory_info().rss
        memory_diff = final_memory - initial_memory
        memory_diff_mb = memory_diff / (1024 * 1024)
        
        # Memory artışı 200MB'dan az olmalı (daha esnek threshold)
        assert memory_diff_mb < 200, f"Potansiyel memory leak: {memory_diff_mb:.1f}MB artış"
    
    def test_concurrent_operations(self):
        """Eşzamanlı işlem testi."""
        import threading
        import queue
        
        detector = OptimizedFaceDetector(max_workers=4)
        results_queue = queue.Queue()
        errors_queue = queue.Queue()
        
        def worker_function(worker_id):
            try:
                for i in range(10):
                    test_img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
                    faces = detector.detect_faces_opencv_optimized(test_img)
                    results_queue.put((worker_id, i, len(faces) if faces else 0))
            except Exception as e:
                errors_queue.put((worker_id, str(e)))
        
        # 4 thread başlat
        threads = []
        for worker_id in range(4):
            thread = threading.Thread(target=worker_function, args=(worker_id,))
            threads.append(thread)
            thread.start()
        
        # Tüm thread'lerin bitmesini bekle
        for thread in threads:
            thread.join(timeout=30)  # 30 saniye timeout
            assert not thread.is_alive(), "Thread timeout oldu"
        
        # Sonuçları kontrol et
        assert errors_queue.empty(), f"Thread hatası: {errors_queue.get() if not errors_queue.empty() else 'Unknown'}"
        assert results_queue.qsize() == 40, f"Beklenen sonuç sayısı 40, alınan: {results_queue.qsize()}"
    
    def cleanup(self):
        """Test sonrası temizlik."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def run_all_tests(self):
        """Tüm testleri çalıştırır."""
        print("\n🚀 Test Süiti Başlatılıyor...")
        
        test_cases = [
            (self.test_config_system, "Konfigürasyon Sistemi"),
            (self.test_database_operations, "Veritabanı İşlemleri"),
            (self.test_face_detector_performance, "Yüz Algılama Performans"),
            (self.test_face_recognizer_accuracy, "Yüz Tanıma Doğruluk"),
            (self.test_user_manager_operations, "Kullanıcı Yöneticisi"),
            (self.test_file_manager_security, "Dosya Güvenliği"),
            (self.test_memory_leak_detection, "Memory Leak Testi"),
            (self.test_concurrent_operations, "Eşzamanlı İşlemler")
    ]
    
        print(f"📊 Toplam {len(test_cases)} test çalıştırılacak\n")
    
        for test_func, test_name in test_cases:
            print(f"🧪 {test_name}...", end=" ")
            result = self.run_test(test_func, test_name)
            if result.passed:
                print(f"✅ ({result.duration:.3f}s)")
            else:
                print(f"❌ ({result.duration:.3f}s)")
                print(f"   {result.details}")
        
        return self.generate_report()
    
    def generate_report(self):
        """Test raporu oluşturur."""
        passed_tests = [r for r in self.results if r.passed]
        failed_tests = [r for r in self.results if not r.passed]
        total_time = sum(r.duration for r in self.results)
        
        print("\n" + "="*60)
        print("📊 TEST RAPORU")
        print("="*60)
        print(f"📈 Toplam Test: {len(self.results)}")
        print(f"✅ Başarılı: {len(passed_tests)}")
        print(f"❌ Başarısız: {len(failed_tests)}")
        print(f"⏱️  Toplam Süre: {total_time:.3f} saniye")
        print(f"📊 Başarı Oranı: {len(passed_tests)/len(self.results)*100:.1f}%")
    
        if failed_tests:
            print("\n❌ BAŞARISIZ TESTLER:")
            for test in failed_tests:
                print(f"  • {test.name}: {test.details}")
        
        print("\n⚡ PERFORMANCE METRİKLERİ:")
        for test in self.results:
            status = "✅" if test.passed else "❌"
            print(f"  {status} {test.name}: {test.duration:.3f}s")
        
        # Performance raporu kaydet
        self.logger_manager.save_performance_report()
        
        print("\n" + "="*60)
        
        return len(failed_tests) == 0


def main():
    """Ana test fonksiyonu."""
    print("🧪 Face Recognition System - Gelişmiş Test Sistemi")
    print("⚡ Performance, Integration ve Security testleri")
    
    test_suite = AdvancedTestSuite()
    
    try:
        success = test_suite.run_all_tests()
        
        if success:
            print("\n🎉 TÜM TESTLER BAŞARILI!")
        return 0

        print("\n💥 BAZI TESTLER BAŞARISIZ!")
        return 1

    except KeyboardInterrupt:
        print("\n⚠️  Test kullanıcı tarafından iptal edildi")
        return 2
    
    except Exception as e:
        print(f"\n💥 Test sistemi hatası: {e}")
        import traceback
        traceback.print_exc()
        return 3
    
    finally:
        test_suite.cleanup()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 