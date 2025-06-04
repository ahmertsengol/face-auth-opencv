#!/usr/bin/env python3
"""
Ana Yüz Tanıma Uygulaması
Clean Architecture ve SOLID prensipleriyle geliştirilmiş yüz tanıma sistemi.
"""

import click
import cv2
import numpy as np
from datetime import datetime
import sys
import os
from pathlib import Path

# Proje root dizinini Python path'ine ekle (scripts dışından çalıştırılırsa)
PROJECT_ROOT = Path(__file__).parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Core modüllerini import et
from core import FaceDetector, FaceRecognizer, UserManager
from core.user_manager import UserData
from core.face_recognizer import RecognitionResult
from utils import CameraManager, FileManager


class FaceRecognitionApp:
    """
    Ana yüz tanıma uygulaması sınıfı.
    Dependency Injection Principle: Bağımlılıklar dışarıdan enjekte edilir.
    """
    
    def __init__(self):
        """Uygulamayı başlatır ve bağımlılıkları enjekte eder."""
        self.face_detector = FaceDetector()
        self.face_recognizer = FaceRecognizer(tolerance=0.6)
        self.user_manager = UserManager()
        self.camera_manager = CameraManager()
        
        # Kayıtlı kullanıcıları yükle
        self._load_known_users()
    
    def _load_known_users(self) -> None:
        """Kayıtlı kullanıcıları sisteme yükler."""
        try:
            users = self.user_manager.load_all_users()
            self.face_recognizer.clear_known_faces()
            
            for user in users:
                for encoding in user.face_encodings:
                    self.face_recognizer.add_known_face(encoding, user.name)
            
            if users:
                print(f"✅ {len(users)} kullanıcı sisteme yüklendi.")
            else:
                print("ℹ️  Henüz kayıtlı kullanıcı yok.")
                
        except Exception as e:
            print(f"❌ Kullanıcılar yüklenirken hata: {e}")
    
    def register_user(self, name: str, sample_count: int = 5) -> bool:
        """
        Yeni kullanıcı kaydeder.
        
        Args:
            name: Kullanıcı adı
            sample_count: Alınacak örnek fotoğraf sayısı
            
        Returns:
            Başarılı ise True, hata varsa False
        """
        if not name or not name.strip():
            print("❌ Geçerli bir isim girmelisiniz!")
            return False
        
        name = name.strip()
        
        # Kullanıcı zaten var mı kontrol et
        if self.user_manager.user_exists(name):
            print(f"⚠️  '{name}' adlı kullanıcı zaten mevcut!")
            return False
        
        print(f"🎯 '{name}' adlı kullanıcı kaydediliyor...")
        print("📷 Kamera başlatılıyor...")
        
        if not self.camera_manager.initialize():
            print("❌ Kamera başlatılamadı!")
            return False
        
        try:
            face_encodings = []
            print(f"📸 {sample_count} adet fotoğraf çekilecek. Her fotoğraf için 's' tuşuna basın.")
            print("❌ Çıkmak için 'q' tuşuna basın.")
            
            sample_taken = 0
            
            while sample_taken < sample_count:
                frame = self.camera_manager.capture_frame()
                if frame is None:
                    continue
                
                # Yüzleri algıla ve çiz
                faces = self.face_detector.detect_faces_opencv(frame)
                
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, f"Sample {sample_taken + 1}/{sample_count}", 
                              (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                
                # Durum bilgisi
                cv2.putText(frame, f"'{name}' - Press 's' to capture, 'q' to quit", 
                          (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, f"Samples: {sample_taken}/{sample_count}", 
                          (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                cv2.imshow('User Registration', frame)
                
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    print("❌ Kayıt iptal edildi.")
                    break
                elif key == ord('s'):
                    # Fotoğraf çek ve encoding al
                    current_encodings = self.face_detector.get_face_encodings(frame)
                    
                    if current_encodings:
                        face_encodings.extend(current_encodings)
                        sample_taken += 1
                        print(f"✅ Örnek {sample_taken}/{sample_count} kaydedildi.")
                    else:
                        print("⚠️  Yüz algılanamadı! Tekrar deneyin.")
            
            cv2.destroyAllWindows()
            
            if sample_taken == 0:
                print("❌ Hiç fotoğraf alınmadı, kayıt iptal edildi.")
                return False
            
            if len(face_encodings) == 0:
                print("❌ Yüz verisi alınamadı, kayıt iptal edildi.")
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
                
                print(f"✅ '{name}' başarıyla kaydedildi! ({len(face_encodings)} yüz örneği)")
                return True
            else:
                print("❌ Kullanıcı kaydedilemedi!")
                return False
        
        except Exception as e:
            print(f"❌ Kayıt sırasında hata: {e}")
            return False
        
        finally:
            self.camera_manager.release()
    
    def start_recognition(self) -> None:
        """Gerçek zamanlı yüz tanıma başlatır."""
        if self.face_recognizer.get_known_faces_count() == 0:
            print("⚠️  Kayıtlı kullanıcı yok! Önce kullanıcı kaydedin.")
            return
        
        print("🎯 Yüz tanıma başlatılıyor...")
        print("❌ Çıkmak için 'q' tuşuna basın.")
        
        if not self.camera_manager.initialize():
            print("❌ Kamera başlatılamadı!")
            return
        
        try:
            while True:
                frame = self.camera_manager.capture_frame()
                if frame is None:
                    continue
                
                # Yüz tespiti (hızlı OpenCV)
                faces = self.face_detector.detect_faces_opencv(frame)
                
                if faces:
                    # Yüz encodinglerini al (doğru tanıma için)
                    face_encodings = self.face_detector.get_face_encodings(frame)
                    
                    # Tanıma yap
                    results = self.face_recognizer.recognize_faces(face_encodings)
                    
                    # Sonuçları çiz
                    for i, (x, y, w, h) in enumerate(faces):
                        if i < len(results):
                            result = results[i]
                            
                            # Renk belirle
                            if result.is_match:
                                color = (0, 255, 0)  # Yeşil - tanındı
                                label = f"{result.user_name} ({result.confidence:.2f})"
                            else:
                                color = (0, 0, 255)  # Kırmızı - tanınmadı
                                label = f"Bilinmeyen ({result.confidence:.2f})"
                            
                            # Çerçeve çiz
                            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                            
                            # İsim etiketi
                            cv2.putText(frame, label, (x, y - 10), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
                # Durum bilgisi
                cv2.putText(frame, f"Registered Users: {self.face_recognizer.get_known_faces_count()}", 
                          (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(frame, "Press 'q' to quit", 
                          (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                cv2.imshow('Face Recognition', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        except Exception as e:
            print(f"❌ Tanıma sırasında hata: {e}")
        
        finally:
            cv2.destroyAllWindows()
            self.camera_manager.release()
            print("👋 Yüz tanıma durduruldu.")
    
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
    app = FaceRecognitionApp()
    app.register_user(name, samples)


@cli.command()
def recognize():
    """Gerçek zamanlı yüz tanıma başlatır"""
    app = FaceRecognitionApp()
    app.start_recognition()


@cli.command('list-users')
def list_users():
    """Kayıtlı kullanıcıları listeler"""
    app = FaceRecognitionApp()
    app.list_users()


@cli.command()
@click.option('--name', '-n', required=True, help='Silinecek kullanıcı adı')
def delete(name: str):
    """Kullanıcıyı siler"""
    app = FaceRecognitionApp()
    
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