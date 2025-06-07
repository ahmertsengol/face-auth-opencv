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
from typing import List, Optional, Tuple

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
    Ultra-optimize edilmiş ana yüz tanıma uygulaması sınıfı.
    Enhanced Features: Stability, adaptive performance, buffer management
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
        
        self.logger.info("🚀 Ultra-optimize edilmiş yüz tanıma sistemi başlatılıyor...")
        
        # Bileşenleri başlat
        self.face_detector = FaceDetector(max_workers=self.config.system.max_workers)
        self.face_recognizer = FaceRecognizer(tolerance=self.config.detection.recognition_tolerance)
        self.user_manager = UserManager(data_dir=self.config.system.data_dir)
        self.camera_manager = CameraManager(camera_index=self.config.camera.index)
        
        # Enhanced Performance tracking
        self.session_stats = {
            'start_time': time.time(),
            'users_processed': 0,
            'faces_detected': 0,
            'recognition_attempts': 0,
            'total_frames': 0,
            'dropped_frames': 0,
            'error_count': 0,
            'cache_hits': 0
        }
        
        # Adaptive Performance Management
        self.performance_monitor = {
            'fps_history': [],
            'processing_times': [],
            'memory_usage': [],
            'target_fps': 25,
            'min_fps': 10,
            'adaptive_quality': True,
            'frame_skip_counter': 0,
            'error_recovery_mode': False
        }
        
        # Frame Buffer Management
        self.frame_buffer = {
            'enabled': True,
            'max_size': 3,
            'current_frames': [],
            'processing_frame': None,
            'last_stable_frame': None
        }
        
        # Stability & Error Recovery
        self.stability_monitor = {
            'consecutive_errors': 0,
            'max_consecutive_errors': 5,
            'last_successful_processing': time.time(),
            'stability_threshold': 30.0,  # seconds
            'auto_recovery_enabled': True
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
    
    def _update_performance_metrics(self, frame_time: float, fps: float, memory_mb: float = 0) -> None:
        """Performance metriklerini günceller ve adaptive ayarları yapar."""
        monitor = self.performance_monitor
        
        # Metric geçmişini güncelle
        monitor['fps_history'].append(fps)
        monitor['processing_times'].append(frame_time)
        monitor['memory_usage'].append(memory_mb)
        
        # Geçmiş boyutunu sınırla (son 100 frame)
        max_history = 100
        for key in ['fps_history', 'processing_times', 'memory_usage']:
            if len(monitor[key]) > max_history:
                monitor[key] = monitor[key][-max_history:]
        
        # Adaptive quality kontrolü
        if monitor['adaptive_quality'] and len(monitor['fps_history']) > 10:
            avg_fps = sum(monitor['fps_history'][-10:]) / 10
            
            # FPS çok düşükse, quality düşür
            if avg_fps < monitor['min_fps']:
                monitor['error_recovery_mode'] = True
                self.logger.warning(f"⚠️ Düşük FPS tespit edildi: {avg_fps:.1f}. Recovery mode aktif.")
            elif avg_fps > monitor['target_fps'] * 0.8:
                monitor['error_recovery_mode'] = False
    
    def _manage_frame_buffer(self, new_frame: np.ndarray) -> Optional[np.ndarray]:
        """Frame buffer yönetimi - stabilite için."""
        buffer = self.frame_buffer
        
        if not buffer['enabled']:
            return new_frame
        
        # Frame'i buffer'a ekle
        if new_frame is not None and new_frame.shape[0] > 0 and new_frame.shape[1] > 0:
            buffer['current_frames'].append(new_frame.copy())
            buffer['last_stable_frame'] = new_frame.copy()
            
            # Buffer boyutunu sınırla
            if len(buffer['current_frames']) > buffer['max_size']:
                buffer['current_frames'].pop(0)
            
            return new_frame
        else:
            # Geçersiz frame - son stabil frame'i kullan
            self.session_stats['dropped_frames'] += 1
            return buffer['last_stable_frame']
    
    def _check_system_stability(self) -> bool:
        """Sistem stabilite kontrolü yapar."""
        stability = self.stability_monitor
        current_time = time.time()
        
        # Son başarılı işlemden beri geçen süre
        time_since_success = current_time - stability['last_successful_processing']
        
        # Çok fazla ardışık hata varsa
        if stability['consecutive_errors'] >= stability['max_consecutive_errors']:
            self.logger.error(f"❌ Çok fazla ardışık hata: {stability['consecutive_errors']}")
            return False
        
        # Uzun süre başarılı işlem yoksa
        if time_since_success > stability['stability_threshold']:
            self.logger.warning(f"⚠️ Uzun süre başarılı işlem yok: {time_since_success:.1f}s")
            return False
        
        return True
    
    def _handle_processing_error(self, error: Exception, context: str) -> None:
        """İşlem hatalarını yönetir ve recovery stratejileri uygular."""
        stability = self.stability_monitor
        stability['consecutive_errors'] += 1
        self.session_stats['error_count'] += 1
        
        self.logger.error(f"❌ {context} hatası: {error}")
        
        # Auto recovery stratejileri
        if stability['auto_recovery_enabled']:
            if stability['consecutive_errors'] >= 3:
                self.logger.info("🔄 Cache temizliği başlatılıyor...")
                self.face_detector.clear_cache()
                
            if stability['consecutive_errors'] >= 5:
                self.logger.info("🔄 Kamera resetleniyor...")
                self.camera_manager.release()
                time.sleep(0.5)
                self.camera_manager.initialize()
    
    def _mark_successful_processing(self) -> None:
        """Başarılı işlem sonrası stabilite metriklerini günceller."""
        stability = self.stability_monitor
        stability['consecutive_errors'] = 0
        stability['last_successful_processing'] = time.time()
    
    def _adaptive_frame_processing(self, frame: np.ndarray, current_fps: float) -> Tuple[List, List]:
        """Adaptive frame processing - FPS'e göre işlem yoğunluğunu ayarlar."""
        faces = []
        results = []
        
        try:
            monitor = self.performance_monitor
            
            # Düşük FPS'de frame atlama
            if monitor['error_recovery_mode'] or current_fps < monitor['min_fps']:
                monitor['frame_skip_counter'] += 1
                if monitor['frame_skip_counter'] % 2 != 0:  # Her ikinci frame'i atla
                    return faces, results
            
            # Normal işleme
            faces = self.face_detector.detect_faces_opencv_optimized(frame, use_cache=True)
            
            if faces:
                # Sadece algılanan yüzlerin encoding'lerini al
                face_locations = [(y, x+w, y+h, x) for x, y, w, h in faces]
                
                # Recovery mode'da daha az jitter kullan
                jitters = 0 if monitor['error_recovery_mode'] else 1
                
                face_encodings = self.face_detector.get_face_encodings_optimized(frame, face_locations)
                
                # Tanıma yap
                if face_encodings:
                    results = self.face_recognizer.recognize_faces(face_encodings)
                    self.session_stats['recognition_attempts'] += len(results)
            
            self._mark_successful_processing()
            
        except Exception as e:
            self._handle_processing_error(e, "Frame işleme")
        
        return faces, results
    
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
                
                # Frame boyutu kontrolü ve debug
                if frame.shape[0] <= 0 or frame.shape[1] <= 0:
                    continue
                
                # Frame kopyalama ve boyut kontrolü
                frame_copy = frame.copy()
                if frame_copy.shape[0] <= 0 or frame_copy.shape[1] <= 0:
                    continue
                
                self.logger.debug(f"✅ Frame boyutu OK: {frame.shape}")
                
                # Optimize yüz algılama
                faces = self.face_detector.detect_faces_opencv_optimized(frame, use_cache=True)
                
                # UI çizimi - Güvenli frame kontrolü ile
                try:
                    # Dashboard UI çiz
                    registration_data = {
                        'mode': 'REGISTRATION',
                        'name': name,
                        'current': sample_taken,
                        'total': sample_count
                    }
                    
                    fps_data = {
                        'fps': 30,  # Registration için sabit FPS
                        'frame_time': 0,
                        'users': self.face_recognizer.get_known_faces_count(),
                        'faces': len(faces),
                        'cache_hits': 0,
                        'memory': 0
                    }
                    
                    # Dashboard UI çizmeden önce frame kontrol et
                    if frame_copy.shape[0] > 0 and frame_copy.shape[1] > 0:
                        frame_copy = self._draw_dashboard_ui(frame_copy, fps_data, registration_data=registration_data)
                        
                        # Yüz overlay'leri çiz
                        if frame_copy.shape[0] > 0 and frame_copy.shape[1] > 0:
                            frame_copy = self._draw_face_overlay(frame_copy, faces, mode='registration')
                    
                    # Final boyut kontrolü
                    if frame_copy.shape[0] > 0 and frame_copy.shape[1] > 0:
                        cv2.imshow('User Registration - Professional Dashboard', frame_copy)
                    else:
                        self.logger.warning(f"⚠️ Final frame boyutu geçersiz: {frame_copy.shape}")
                        # Fallback: sadece orijinal frame'i göster
                        cv2.imshow('User Registration - Professional Dashboard', frame)
                        
                except Exception as ui_error:
                    self.logger.error(f"❌ UI çizim hatası: {ui_error}")
                    # Fallback: basit UI ile devam et
                    for (x, y, w, h) in faces:
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, f"Sample {sample_taken}/{sample_count}", (10, 30), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    cv2.imshow('User Registration - Professional Dashboard', frame)
                
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
        """Ultra-optimize edilmiş adaptive gerçek zamanlı yüz tanıma."""
        if self.face_recognizer.get_known_faces_count() == 0:
            self.logger.warning("⚠️  Kayıtlı kullanıcı yok! Önce kullanıcı kaydedin.")
            return
        
        self.logger.info("🎯 Adaptive yüz tanıma başlatılıyor...")
        
        if not self.camera_manager.initialize():
            self.logger.error("❌ Kamera başlatılamadı!")
            return
        
        # Enhanced Performance tracking
        fps_counter = 0
        fps_start_time = time.time()
        last_recognition_result = None
        stability_check_interval = 30  # 30 frame'de bir stabilite kontrolü
        
        try:
            while True:
                # Stabilite kontrolü
                if fps_counter % stability_check_interval == 0:
                    if not self._check_system_stability():
                        self.logger.warning("⚠️ Sistem instabil, recovery stratejileri uygulanıyor...")
                        continue
                
                # Frame capture with buffer management
                raw_frame = self.camera_manager.capture_frame()
                frame = self._manage_frame_buffer(raw_frame)
                
                if frame is None:
                    continue
                
                self.session_stats['total_frames'] += 1
                frame_start_time = time.time()
                
                # Performance hesaplamaları (önce)
                fps_counter += 1
                current_time = time.time()
                
                if fps_counter % 10 == 0:
                    elapsed = current_time - fps_start_time
                    current_fps = fps_counter / elapsed if elapsed > 0 else 0
                    fps_counter = 0
                    fps_start_time = current_time
                else:
                    elapsed = current_time - fps_start_time
                    current_fps = fps_counter / elapsed if elapsed > 0 and fps_counter > 0 else 0
                
                # Adaptive frame processing
                faces, results = self._adaptive_frame_processing(frame, current_fps)
                
                # Son tanıma sonucunu kaydet
                if results:
                    last_recognition_result = {
                        'name': results[0].user_name if results[0].is_match else 'Bilinmeyen',
                        'confidence': results[0].confidence,
                        'is_match': results[0].is_match
                    }
                
                # Frame processing time
                frame_time = (time.time() - frame_start_time) * 1000
                
                # Performance metrics güncelle
                import psutil
                memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
                self._update_performance_metrics(frame_time, current_fps, memory_mb)
                
                # Cache statistikleri
                cache_stats = self.face_detector.get_performance_stats()
                
                # Enhanced Dashboard UI with stability info
                try:
                    fps_data = {
                        'fps': current_fps,
                        'frame_time': frame_time,
                        'users': self.face_recognizer.get_known_faces_count(),
                        'faces': len(faces),
                        'cache_hits': cache_stats.get('cache_size', 0),
                        'memory': memory_mb,
                        'recovery_mode': self.performance_monitor['error_recovery_mode'],
                        'dropped_frames': self.session_stats['dropped_frames'],
                        'total_frames': self.session_stats['total_frames']
                    }
                    
                    recognition_data = {
                        'last_recognition': last_recognition_result,
                        'stability': {
                            'errors': self.stability_monitor['consecutive_errors'],
                            'success_time': time.time() - self.stability_monitor['last_successful_processing']
                        }
                    }
                    
                    # Safe UI rendering
                    if frame.shape[0] > 0 and frame.shape[1] > 0:
                        frame = self._draw_dashboard_ui(frame, fps_data, recognition_data=recognition_data)
                        
                        # Yüz overlay'leri çiz
                        if frame.shape[0] > 0 and frame.shape[1] > 0:
                            frame = self._draw_face_overlay(frame, faces, results, mode='recognition')
                    
                    # Final display
                    if frame.shape[0] > 0 and frame.shape[1] > 0:
                        cv2.imshow('Ultra-Optimized Face Recognition', frame)
                    else:
                        self.logger.debug("⚠️ Frame boyutu geçersiz, atlanıyor")
                        
                except Exception as ui_error:
                    self._handle_processing_error(ui_error, "UI rendering")
                    # Minimal fallback
                    try:
                        cv2.imshow('Ultra-Optimized Face Recognition', frame)
                    except:
                        pass
                
                # Enhanced keyboard controls
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    # Full system reset
                    self.face_detector.clear_cache()
                    self.performance_monitor['error_recovery_mode'] = False
                    self.stability_monitor['consecutive_errors'] = 0
                    self.logger.info("🔄 Sistem sıfırlandı.")
                elif key == ord('s') and faces:
                    # Enhanced screenshot with metadata
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    screenshot_path = f"screenshots/recognition_{timestamp}.jpg"
                    os.makedirs("screenshots", exist_ok=True)
                    cv2.imwrite(screenshot_path, frame)
                    
                    # Save metadata
                    metadata = {
                        'timestamp': timestamp,
                        'faces_count': len(faces),
                        'recognition_results': [r.__dict__ for r in results] if results else [],
                        'fps': current_fps,
                        'memory_mb': memory_mb
                    }
                    import json
                    with open(f"screenshots/metadata_{timestamp}.json", 'w') as f:
                        json.dump(metadata, f, indent=2, default=str)
                    
                    self.logger.info(f"📸 Screenshot ve metadata kaydedildi: {screenshot_path}")
                elif key == ord('a'):
                    # Toggle adaptive mode
                    self.performance_monitor['adaptive_quality'] = not self.performance_monitor['adaptive_quality']
                    status = "açık" if self.performance_monitor['adaptive_quality'] else "kapalı"
                    self.logger.info(f"🔧 Adaptive mode: {status}")
        
        except Exception as e:
            self._handle_processing_error(e, "Ana recognition loop")
        
        finally:
            cv2.destroyAllWindows()
            self.camera_manager.release()
            self._save_enhanced_session_stats()
            self.logger.info("👋 Ultra-optimized yüz tanıma durduruldu.")
    
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

    def _save_enhanced_session_stats(self):
        """Enhanced session istatistiklerini kaydet."""
        session_duration = time.time() - self.session_stats['start_time']
        
        # Enhanced istatistikler
        total_frames = self.session_stats['total_frames']
        dropped_frames = self.session_stats['dropped_frames']
        error_count = self.session_stats['error_count']
        
        success_rate = ((total_frames - error_count) / total_frames * 100) if total_frames > 0 else 0
        drop_rate = (dropped_frames / total_frames * 100) if total_frames > 0 else 0
        
        # Performance metrikleri
        monitor = self.performance_monitor
        avg_fps = sum(monitor['fps_history']) / len(monitor['fps_history']) if monitor['fps_history'] else 0
        avg_processing_time = sum(monitor['processing_times']) / len(monitor['processing_times']) if monitor['processing_times'] else 0
        avg_memory = sum(monitor['memory_usage']) / len(monitor['memory_usage']) if monitor['memory_usage'] else 0
        
        self.logger.info("📊 Enhanced Session İstatistikleri:")
        self.logger.info("=" * 50)
        self.logger.info(f"⏱️  Süre: {session_duration:.1f} saniye")
        self.logger.info(f"👥 İşlenen kullanıcı: {self.session_stats['users_processed']}")
        self.logger.info(f"👁️  Algılanan yüz: {self.session_stats['faces_detected']}")
        self.logger.info(f"🎯 Tanıma denemesi: {self.session_stats['recognition_attempts']}")
        self.logger.info(f"📺 Toplam frame: {total_frames}")
        self.logger.info(f"📉 Atılan frame: {dropped_frames} ({drop_rate:.1f}%)")
        self.logger.info(f"❌ Hata sayısı: {error_count}")
        self.logger.info(f"✅ Başarı oranı: {success_rate:.1f}%")
        self.logger.info(f"🎮 Ortalama FPS: {avg_fps:.1f}")
        self.logger.info(f"⚡ Ortalama işlem süresi: {avg_processing_time:.1f}ms")
        self.logger.info(f"💾 Ortalama memory: {avg_memory:.1f}MB")
        self.logger.info(f"🔄 Recovery mode kullanım: {'Evet' if monitor['error_recovery_mode'] else 'Hayır'}")
        
        # Stability metrikleri
        stability = self.stability_monitor
        self.logger.info(f"🛡️  Son hata: {stability['consecutive_errors']} ardışık")
        self.logger.info(f"🕐 Son başarılı işlem: {time.time() - stability['last_successful_processing']:.1f}s önce")
        
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

    def _draw_dashboard_ui(self, frame, fps_data, recognition_data=None, registration_data=None):
        """
        Minimal ve temiz dashboard UI çizer.
        
        Args:
            frame: Video frame
            fps_data: FPS ve performance verileri
            recognition_data: Tanıma verileri (opsiyonel)
            registration_data: Kayıt verileri (opsiyonel)
        """
        # Frame boyutu kontrolü
        if frame is None or frame.shape[0] <= 0 or frame.shape[1] <= 0:
            self.logger.warning(f"⚠️ Dashboard: Geçersiz frame boyutu: {frame.shape if frame is not None else 'None'}")
            return frame
        
        try:
            height, width = frame.shape[:2]
            
            # Minimum boyut kontrolü
            if height < 200 or width < 200:
                self.logger.warning(f"⚠️ Dashboard: Frame çok küçük: {width}x{height}")
                return frame
            
            # Modern color scheme
            colors = {
                'primary': (240, 180, 50),      # Modern blue
                'success': (50, 205, 50),       # Lime green
                'warning': (50, 180, 255),      # Orange
                'danger': (50, 50, 255),        # Red
                'dark': (40, 40, 40),           # Dark gray
                'white': (255, 255, 255),       # White
                'black': (0, 0, 0)              # Black
            }
            
            # 1. Minimal Top Bar - Sadece temel bilgiler
            top_bar_height = 40
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (width, top_bar_height), colors['dark'], -1)
            cv2.addWeighted(frame, 0.7, overlay, 0.3, 0, frame)
            
            # Mod göstergesi (sol üst)
            mode = registration_data['mode'] if registration_data else 'RECOGNITION'
            mode_color = colors['warning'] if mode == 'REGISTRATION' else colors['success']
            cv2.putText(frame, mode, (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, mode_color, 2)
            
            # FPS göstergesi (sağ üst) - adaptive mode dahil
            current_fps = fps_data.get('fps', 0)
            recovery_mode = fps_data.get('recovery_mode', False)
            
            # FPS rengi - recovery mode'da turuncu
            if recovery_mode:
                fps_color = colors['warning']
                fps_text = f"FPS: {current_fps:.0f} (A)"  # A = Adaptive
            else:
                fps_color = colors['success'] if current_fps >= 20 else colors['warning'] if current_fps >= 10 else colors['danger']
                fps_text = f"FPS: {current_fps:.0f}"
                
            cv2.putText(frame, fps_text, (width - 120, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, fps_color, 1)
            
            # 2. Registration specific minimal UI
            if registration_data:
                # Sadece progress göster (sol alt)
                progress_text = f"{registration_data['current']}/{registration_data['total']}"
                cv2.putText(frame, progress_text, (15, height - 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, colors['primary'], 2)
                
                # Kullanıcı adı (alt merkez)
                user_text = f"Kayit: {registration_data['name']}"
                text_size = cv2.getTextSize(user_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                text_x = (width - text_size[0]) // 2
                cv2.putText(frame, user_text, (text_x, height - 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, colors['white'], 2)
                
                # Minimal kontrol ipucu (sağ alt)
                cv2.putText(frame, "S: Cek", (width - 80, height - 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors['white'], 1)
                cv2.putText(frame, "Q: Cik", (width - 80, height - 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors['white'], 1)
            
            # 3. Recognition specific minimal UI
            if recognition_data and recognition_data.get('last_recognition'):
                # Son tanıma sonucu (alt merkez)
                last_result = recognition_data['last_recognition']
                result_color = colors['success'] if last_result.get('is_match') else colors['danger']
                result_text = f"{last_result.get('name', 'Bilinmeyen')} ({last_result.get('confidence', 0):.2f})"
                text_size = cv2.getTextSize(result_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                text_x = (width - text_size[0]) // 2
                cv2.putText(frame, result_text, (text_x, height - 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, result_color, 2)
                
                # Minimal kontrol ipucu (sağ alt)
                cv2.putText(frame, "Q: Cik", (width - 60, height - 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors['white'], 1)
                
                cv2.putText(frame, "R: Reset", (width - 130, height - 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors['white'], 1)
                
                cv2.putText(frame, "S: Cek", (width - 190, height - 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors['white'], 1)
                
                cv2.putText(frame, "A: Auto", (width - 250, height - 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors['white'], 1)
            
            return frame
        
        except Exception as e:
            self.logger.error(f"❌ Dashboard çizim hatası: {e}")
            return frame
    
    def _draw_face_overlay(self, frame, faces, results=None, mode='recognition'):
        """
        Yüz çerçeveleri ve minimal etiketleri çizer.
        
        Args:
            frame: Video frame
            faces: Algılanan yüzler
            results: Tanıma sonuçları
            mode: Mod ('recognition' veya 'registration')
        """
        # Frame boyutu kontrolü
        if frame is None or frame.shape[0] <= 0 or frame.shape[1] <= 0:
            self.logger.warning(f"⚠️ Face Overlay: Geçersiz frame boyutu")
            return frame
        
        if not faces:
            return frame
        
        try:
            colors = {
                'success': (50, 205, 50),
                'danger': (50, 50, 255),
                'warning': (50, 180, 255),
                'primary': (240, 180, 50)
            }
            
            for i, (x, y, w, h) in enumerate(faces):
                if mode == 'registration':
                    # Registration mode - basit yeşil çerçeve
                    color = colors['success']
                    label = ""  # Kayıt modunda yazı yok
                else:
                    # Recognition mode
                    if results and i < len(results):
                        result = results[i]
                        if result.is_match:
                            color = colors['success']
                            label = result.user_name
                        else:
                            color = colors['danger']
                            label = "?"
                    else:
                        color = colors['warning']
                        label = "..."
                
                # Basit çerçeve çiz
                thickness = 2
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)
                
                # Sadece recognition modunda ve eğer label varsa yazı göster
                if mode == 'recognition' and label:
                    # Küçük yazı etiketi - sadece üst kısımda
                    font_scale = 0.6
                    font_thickness = 1
                    text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)[0]
                    
                    # Etiket pozisyonu
                    label_x = x
                    label_y = y - 10
                    
                    # Eğer etiket frame dışına çıkıyorsa, kutunun içine al
                    if label_y < 15:
                        label_y = y + 20
                    
                    # Yazı arkaplanı (küçük)
                    padding = 3
                    cv2.rectangle(frame, 
                                (label_x - padding, label_y - text_size[1] - padding), 
                                (label_x + text_size[0] + padding, label_y + padding), 
                                color, -1)
                    
                    # Yazı
                    cv2.putText(frame, label, (label_x, label_y), 
                              cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thickness)
            
            return frame
        
        except Exception as e:
            self.logger.error(f"❌ Face Overlay çizim hatası: {e}")
            return frame


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