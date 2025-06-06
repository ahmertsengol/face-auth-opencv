#!/usr/bin/env python3
"""
Ana Yüz Tanıma Uygulaması - Optimize Edilmiş Versiyon
Clean Architecture ve SOLID prensipleriyle geliştirilmiş yüz tanıma sistemi.
"""

import click
import cv2
import numpy as np
from datetime import datetime
import sys
import os
from pathlib import Path
import time
from tqdm import tqdm

# Proje root dizinini Python path'ine ekle (scripts dışından çalıştırılırsa)
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Core modüllerini import et
from core import FaceDetector, FaceRecognizer, UserManager
from core.user_manager import UserData
from core.face_recognizer import RecognitionResult
from utils import CameraManager, FileManager

# Yeni optimize bileşenler
from config.app_config import get_config, get_config_manager
from utils.logger import setup_logging, get_logger, log_execution_time


class OptimizedFaceRecognitionApp:
    """
    Optimize edilmiş ana yüz tanıma uygulaması sınıfı.
    Performance improvements: Config management, logging, caching
    """
    
    def __init__(self):
        """Uygulamayı başlatır ve bağımlılıkları enjekte eder."""
        # Logging ve config sistemini başlat
        self.config = get_config()
        self.logger_manager = setup_logging(
            log_dir=self.config.system.logs_dir,
            log_level=self.config.system.log_level
        )
        self.logger = get_logger('app')
        
        self.logger.info("🚀 Optimize edilmiş yüz tanıma sistemi başlatılıyor...")
        
        # Bileşenleri başlat
        self.face_detector = FaceDetector(max_workers=self.config.system.max_workers)
        self.face_recognizer = FaceRecognizer(tolerance=self.config.detection.recognition_tolerance)
        self.user_manager = UserManager(data_dir=self.config.system.data_dir)
        self.camera_manager = CameraManager(camera_index=self.config.camera.index)
        
        # Performance metrics
        self.session_stats = {
            'start_time': time.time(),
            'users_processed': 0,
            'faces_detected': 0,
            'recognition_attempts': 0
        }
        
        # Kayıtlı kullanıcıları yükle
        self._load_known_users()
    
    @log_execution_time('app')
    def _load_known_users(self) -> None:
        """Kayıtlı kullanıcıları sisteme yükler."""
        try:
            users = self.user_manager.load_all_users()
            self.face_recognizer.clear_known_faces()
            
            if users:
                self.logger.info(f"📚 {len(users)} kullanıcı yükleniyor...")
                
                # Progress bar ile yükleme
                for user in tqdm(users, desc="Kullanıcılar yükleniyor", disable=len(users) < 5):
                    for encoding in user.face_encodings:
                        self.face_recognizer.add_known_face(encoding, user.name)
                
                self.logger.info(f"✅ {len(users)} kullanıcı sisteme yüklendi.")
            else:
                self.logger.info("ℹ️  Henüz kayıtlı kullanıcı yok.")
                
        except Exception as e:
            self.logger.error(f"❌ Kullanıcılar yüklenirken hata: {e}")
    
    @log_execution_time('app')
    def register_user(self, name: str, sample_count: int = None) -> bool:
        """
        Optimize edilmiş kullanıcı kayıt sistemi.
        
        Args:
            name: Kullanıcı adı
            sample_count: Alınacak örnek fotoğraf sayısı
            
        Returns:
            Başarılı ise True, hata varsa False
        """
        if sample_count is None:
            sample_count = 5  # Default
            
        if not name or not name.strip():
            self.logger.error("❌ Geçerli bir isim girmelisiniz!")
            return False
        
        name = name.strip()
        
        # Kullanıcı zaten var mı kontrol et
        if self.user_manager.user_exists(name):
            self.logger.warning(f"⚠️  '{name}' adlı kullanıcı zaten mevcut!")
            return False
        
        self.logger.info(f"🎯 '{name}' adlı kullanıcı kaydediliyor...")
        
        # Kamera ayarlarını uygula
        if not self.camera_manager.initialize():
            self.logger.error("❌ Kamera başlatılamadı!")
            return False
        
        # Kamera optimizasyonları
        self.camera_manager.set_resolution(
            self.config.camera.width, 
            self.config.camera.height
        )
        
        try:
            face_encodings = []
            sample_taken = 0
            
            self.logger.info(f"📸 {sample_count} adet fotoğraf çekilecek...")
            print("Her fotoğraf için 's' tuşuna basın. Çıkmak için 'q'.")
            
            # Progress tracking
            progress_bar = tqdm(total=sample_count, desc="Örnekler", position=0)
            
            while sample_taken < sample_count:
                frame = self.camera_manager.capture_frame()
                if frame is None:
                    continue
                
                # Optimize yüz algılama
                faces = self.face_detector.detect_faces_opencv_optimized(frame, use_cache=True)
                
                # UI çizimi
                frame_copy = frame.copy()
                for (x, y, w, h) in faces:
                    color = self.config.ui.success_color
                    cv2.rectangle(frame_copy, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(frame_copy, f"Sample {sample_taken + 1}/{sample_count}", 
                              (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                
                # Durum bilgisi
                status_text = f"'{name}' - Press 's' to capture, 'q' to quit"
                cv2.putText(frame_copy, status_text, (10, 30), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.config.ui.text_color, 2)
                cv2.putText(frame_copy, f"Samples: {sample_taken}/{sample_count}", 
                          (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.config.ui.text_color, 2)
                
                # Performance bilgisi
                if self.config.ui.show_fps:
                    fps_text = f"Detection: {len(faces)} faces"
                    cv2.putText(frame_copy, fps_text, (10, frame_copy.shape[0] - 20), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.config.ui.text_color, 1)
                
                cv2.imshow('User Registration', frame_copy)
                
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    self.logger.info("❌ Kayıt iptal edildi.")
                    break
                elif key == ord('s') and faces:
                    # Optimize encoding çıkarma
                    current_encodings = self.face_detector.get_face_encodings_optimized(frame)
                    
                    if current_encodings:
                        face_encodings.extend(current_encodings)
                        sample_taken += 1
                        progress_bar.update(1)
                        self.logger.debug(f"✅ Örnek {sample_taken}/{sample_count} kaydedildi.")
                        self.session_stats['faces_detected'] += len(current_encodings)
                    else:
                        self.logger.warning("⚠️  Yüz encoding'i alınamadı! Tekrar deneyin.")
                elif key == ord('s') and not faces:
                    self.logger.warning("⚠️  Yüz algılanamadı! Tekrar deneyin.")
            
            progress_bar.close()
            cv2.destroyAllWindows()
            
            if sample_taken == 0:
                self.logger.error("❌ Hiç fotoğraf alınmadı, kayıt iptal edildi.")
                return False
            
            if len(face_encodings) == 0:
                self.logger.error("❌ Yüz verisi alınamadı, kayıt iptal edildi.")
                return False
            
            # Kullanıcı verilerini kaydet
            user_data = UserData(
                name=name,
                face_encodings=face_encodings,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            if self.user_manager.save_user(user_data):
                # Tanıma sistemine ekle
                for encoding in face_encodings:
                    self.face_recognizer.add_known_face(encoding, name)
                
                self.logger.info(f"✅ '{name}' başarıyla kaydedildi! ({len(face_encodings)} yüz örneği)")
                self.session_stats['users_processed'] += 1
                return True
            else:
                self.logger.error("❌ Kullanıcı kaydedilemedi!")
                return False
        
        except Exception as e:
            self.logger.error(f"❌ Kayıt sırasında hata: {e}")
            return False
        
        finally:
            self.camera_manager.release()
    
    @log_execution_time('app')
    def start_recognition(self) -> None:
        """Optimize edilmiş gerçek zamanlı yüz tanıma."""
        if self.face_recognizer.get_known_faces_count() == 0:
            self.logger.warning("⚠️  Kayıtlı kullanıcı yok! Önce kullanıcı kaydedin.")
            return
        
        self.logger.info("🎯 Yüz tanıma başlatılıyor...")
        
        if not self.camera_manager.initialize():
            self.logger.error("❌ Kamera başlatılamadı!")
            return
        
        # Performance tracking
        fps_counter = 0
        fps_start_time = time.time()
        
        try:
            while True:
                frame = self.camera_manager.capture_frame()
                if frame is None:
                    continue
                
                frame_start_time = time.time()
                
                # Optimize yüz tespiti
                faces = self.face_detector.detect_faces_opencv_optimized(frame, use_cache=True)
                
                if faces:
                    # Sadece algılanan yüzlerin encoding'lerini al
                    face_locations = [(y, x+w, y+h, x) for x, y, w, h in faces]  # Convert format
                    face_encodings = self.face_detector.get_face_encodings_optimized(frame, face_locations)
                    
                    # Tanıma yap
                    results = self.face_recognizer.recognize_faces(face_encodings)
                    self.session_stats['recognition_attempts'] += len(results)
                    
                    # Sonuçları çiz
                    for i, (x, y, w, h) in enumerate(faces):
                        if i < len(results):
                            result = results[i]
                            
                            # Renk ve etiket belirle
                            if result.is_match:
                                color = self.config.ui.success_color
                                confidence_text = f" ({result.confidence:.2f})" if self.config.ui.show_confidence else ""
                                label = f"{result.user_name}{confidence_text}"
                            else:
                                color = self.config.ui.error_color
                                confidence_text = f" ({result.confidence:.2f})" if self.config.ui.show_confidence else ""
                                label = f"Bilinmeyen{confidence_text}"
                            
                            # Çerçeve ve etiket çiz
                            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                            cv2.putText(frame, label, (x, y - 10), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
                # Performance bilgilerini çiz
                if self.config.ui.show_fps:
                    # FPS hesaplama
                    fps_counter += 1
                    if fps_counter % 30 == 0:  # Her 30 frame'de bir güncelle
                        current_fps = fps_counter / (time.time() - fps_start_time)
                        fps_counter = 0
                        fps_start_time = time.time()
                    else:
                        current_fps = fps_counter / (time.time() - fps_start_time) if fps_counter > 0 else 0
                    
                    # Performance metrikler
                    frame_time = (time.time() - frame_start_time) * 1000  # ms
                    
                    # Bilgileri çiz
                    info_lines = [
                        f"Users: {self.face_recognizer.get_known_faces_count()}",
                        f"FPS: {current_fps:.1f}",
                        f"Frame: {frame_time:.1f}ms",
                        f"Faces: {len(faces) if faces else 0}",
                        "Press 'q' to quit"
                    ]
                    
                    for i, line in enumerate(info_lines):
                        y_pos = 30 + i * 25
                        cv2.putText(frame, line, (10, y_pos), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.config.ui.text_color, 2)
                
                cv2.imshow('Face Recognition', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        except Exception as e:
            self.logger.error(f"❌ Tanıma sırasında hata: {e}")
        
        finally:
            cv2.destroyAllWindows()
            self.camera_manager.release()
            self._save_session_stats()
            self.logger.info("👋 Yüz tanıma durduruldu.")
    
    def _save_session_stats(self):
        """Session istatistiklerini kaydet."""
        session_duration = time.time() - self.session_stats['start_time']
        
        self.logger.info("📊 Session İstatistikleri:")
        self.logger.info(f"  Süre: {session_duration:.1f} saniye")
        self.logger.info(f"  İşlenen kullanıcı: {self.session_stats['users_processed']}")
        self.logger.info(f"  Algılanan yüz: {self.session_stats['faces_detected']}")
        self.logger.info(f"  Tanıma denemesi: {self.session_stats['recognition_attempts']}")
        
        # Performance raporu kaydet
        self.logger_manager.save_performance_report()

    def list_users(self) -> None:
        """Kayıtlı kullanıcıları listeler."""
        users = self.user_manager.load_all_users()
        
        if not users:
            print("📭 Kayıtlı kullanıcı bulunamadı.")
            return
        
        print(f"\n👥 Kayıtlı Kullanıcılar ({len(users)} adet):")
        print("=" * 50)
        
        for i, user in enumerate(users, 1):
            print(f"{i}. 👤 {user.name}")
            print(f"   📸 Yüz örnekleri: {len(user.face_encodings)}")
            print(f"   📅 Kayıt tarihi: {user.created_at}")
            print(f"   🔄 Güncellenme: {user.updated_at}")
            print("-" * 30)
    
    def delete_user(self, name: str) -> bool:
        """
        Kullanıcıyı siler.
        
        Args:
            name: Silinecek kullanıcının adı
            
        Returns:
            Başarılı ise True, hata varsa False
        """
        if not name or not name.strip():
            print("❌ Geçerli bir isim girmelisiniz!")
            return False
        
        name = name.strip()
        
        if not self.user_manager.user_exists(name):
            print(f"⚠️  '{name}' adlı kullanıcı bulunamadı!")
            return False
        
        if self.user_manager.delete_user(name):
            # Tanıma sisteminden de kaldır
            self.face_recognizer.remove_known_face(name)
            print(f"✅ '{name}' başarıyla silindi.")
            return True
        else:
            print(f"❌ '{name}' silinemedi!")
            return False


# CLI Komutları
@click.group()
def cli():
    """👤 Yüz Tanıma Sistemi - OpenCV ile basit ama etkili yüz tanıma"""
    pass


@cli.command()
@click.option('--name', '-n', required=True, help='Kullanıcı adı')
@click.option('--samples', '-s', default=5, help='Alınacak örnek sayısı (varsayılan: 5)')
def register(name: str, samples: int):
    """Yeni kullanıcı kaydeder"""
    app = OptimizedFaceRecognitionApp()
    app.register_user(name, samples)


@cli.command()
def recognize():
    """Gerçek zamanlı yüz tanıma başlatır"""
    app = OptimizedFaceRecognitionApp()
    app.start_recognition()


@cli.command('list-users')
def list_users():
    """Kayıtlı kullanıcıları listeler"""
    app = OptimizedFaceRecognitionApp()
    app.list_users()


@cli.command()
@click.option('--name', '-n', required=True, help='Silinecek kullanıcı adı')
def delete(name: str):
    """Kullanıcıyı siler"""
    app = OptimizedFaceRecognitionApp()
    
    # Onay iste
    if click.confirm(f"'{name}' adlı kullanıcıyı silmek istediğinizden emin misiniz?"):
        app.delete_user(name)
    else:
        print("❌ İşlem iptal edildi.")


@cli.command()
def test():
    """Sistem testini yapar"""
    print("🔧 Sistem testi başlatılıyor...")
    
    # Kamera testi
    print("\n📷 Kamera testi:")
    camera = CameraManager()
    if camera.test_camera():
        print("✅ Kamera testi başarılı!")
    else:
        print("❌ Kamera testi başarısız!")
    camera.release()
    
    # Face detection testi
    print("\n🤖 Yüz algılama testi:")
    try:
        detector = FaceDetector()
        print("✅ Yüz algılama modeli yüklendi!")
    except Exception as e:
        print(f"❌ Yüz algılama hatası: {e}")
    
    # Dosya sistemi testi
    print("\n💾 Dosya sistemi testi:")
    if FileManager.ensure_directory("data/users"):
        print("✅ Veri dizini hazır!")
    else:
        print("❌ Veri dizini oluşturulamadı!")
    
    print("\n✅ Sistem testi tamamlandı!")


if __name__ == '__main__':
    try:
        cli()
    except KeyboardInterrupt:
        print("\n👋 Uygulama kapatıldı.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")
        sys.exit(1) 