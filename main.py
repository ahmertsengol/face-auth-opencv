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
                
                # Frame boyutu kontrolü
                if frame.shape[0] <= 0 or frame.shape[1] <= 0:
                    continue
                
                frame_start_time = time.time()
                
                # Optimize yüz algılama
                faces = self.face_detector.detect_faces_opencv_optimized(frame, use_cache=True)
                
                # UI çizimi
                frame_copy = frame.copy()
                
                # Dashboard UI çiz
                registration_data = {
                    'mode': 'REGISTRATION',
                    'name': name,
                    'current': sample_taken,
                    'total': sample_count
                }
                
                fps_data = {
                    'fps': 30,  # Registration için sabit FPS
                    'frame_time': (time.time() - time.time()) * 1000,
                    'users': self.face_recognizer.get_known_faces_count(),
                    'faces': len(faces),
                    'cache_hits': 0,
                    'memory': 0
                }
                
                frame_copy = self._draw_dashboard_ui(frame_copy, fps_data, registration_data=registration_data)
                
                # Yüz overlay'leri çiz
                frame_copy = self._draw_face_overlay(frame_copy, faces, mode='registration')
                
                cv2.imshow('User Registration - Professional Dashboard', frame_copy)
                
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
        last_recognition_result = None
        
        try:
            while True:
                frame = self.camera_manager.capture_frame()
                if frame is None:
                    continue
                
                # Frame boyutu kontrolü
                if frame.shape[0] <= 0 or frame.shape[1] <= 0:
                    continue
                
                frame_start_time = time.time()
                
                # Optimize yüz tespiti
                faces = self.face_detector.detect_faces_opencv_optimized(frame, use_cache=True)
                
                results = []
                if faces:
                    # Sadece algılanan yüzlerin encoding'lerini al
                    face_locations = [(y, x+w, y+h, x) for x, y, w, h in faces]  # Convert format
                    face_encodings = self.face_detector.get_face_encodings_optimized(frame, face_locations)
                    
                    # Tanıma yap
                    results = self.face_recognizer.recognize_faces(face_encodings)
                    self.session_stats['recognition_attempts'] += len(results)
                    
                    # Son tanıma sonucunu kaydet
                    if results:
                        last_recognition_result = {
                            'name': results[0].user_name if results[0].is_match else 'Unknown',
                            'confidence': results[0].confidence,
                            'is_match': results[0].is_match
                        }
                
                # Performance hesaplamaları
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
                
                frame_time = (current_time - frame_start_time) * 1000
                cache_stats = self.face_detector.get_performance_stats()
                
                # Dashboard UI çiz
                fps_data = {
                    'fps': current_fps,
                    'frame_time': frame_time,
                    'users': self.face_recognizer.get_known_faces_count(),
                    'faces': len(faces),
                    'cache_hits': cache_stats.get('cache_hits', 0),
                    'memory': cache_stats.get('memory_usage', 0)
                }
                
                recognition_data = {
                    'last_recognition': last_recognition_result
                }
                
                frame = self._draw_dashboard_ui(frame, fps_data, recognition_data=recognition_data)
                
                # Yüz overlay'leri çiz
                frame = self._draw_face_overlay(frame, faces, results, mode='recognition')
                
                cv2.imshow('Face Recognition - Professional Dashboard', frame)
                
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    # Cache reset
                    self.face_detector.clear_cache()
                    self.logger.info("🔄 Cache temizlendi.")
                elif key == ord('s') and faces:
                    # Screenshot
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    screenshot_path = f"screenshots/recognition_{timestamp}.jpg"
                    os.makedirs("screenshots", exist_ok=True)
                    cv2.imwrite(screenshot_path, frame)
                    self.logger.info(f"📸 Screenshot kaydedildi: {screenshot_path}")
        
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

    def _draw_dashboard_ui(self, frame, fps_data, recognition_data=None, registration_data=None):
        """
        Professional dashboard UI çizer.
        
        Args:
            frame: Video frame
            fps_data: FPS ve performance verileri
            recognition_data: Tanıma verileri (opsiyonel)
            registration_data: Kayıt verileri (opsiyonel)
        """
        height, width = frame.shape[:2]
        
        # Modern color scheme
        colors = {
            'primary': (240, 180, 50),      # Modern blue
            'secondary': (200, 200, 200),   # Light gray
            'success': (50, 205, 50),       # Lime green
            'warning': (50, 180, 255),      # Orange
            'danger': (50, 50, 255),        # Red
            'dark': (30, 30, 30),           # Dark gray
            'white': (255, 255, 255),       # White
            'black': (0, 0, 0)              # Black
        }
        
        # 1. Top Status Bar
        status_height = 60
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (width, status_height), colors['dark'], -1)
        cv2.addWeighted(frame, 0.3, overlay, 0.7, 0, frame)
        
        # Status bar content
        app_title = "Face Recognition System v2.0.2"
        cv2.putText(frame, app_title, (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, colors['primary'], 2)
        
        # Current time
        current_time = datetime.now().strftime("%H:%M:%S")
        time_text = f"Time: {current_time}"
        cv2.putText(frame, time_text, (width - 150, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors['white'], 1)
        
        # 2. Performance Panel (Right Side)
        panel_width = 300
        panel_height = 250
        panel_x = width - panel_width - 10
        panel_y = status_height + 10
        
        # Panel background
        overlay = frame.copy()
        cv2.rectangle(overlay, (panel_x, panel_y), (panel_x + panel_width, panel_y + panel_height), colors['dark'], -1)
        cv2.addWeighted(frame, 0.8, overlay, 0.2, 0, frame)
        
        # Panel border
        cv2.rectangle(frame, (panel_x, panel_y), (panel_x + panel_width, panel_y + panel_height), colors['primary'], 2)
        
        # Panel title
        cv2.putText(frame, "PERFORMANCE MONITOR", (panel_x + 10, panel_y + 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors['primary'], 2)
        
        # FPS Gauge
        gauge_x = panel_x + 20
        gauge_y = panel_y + 50
        gauge_width = 260
        gauge_height = 25
        
        # FPS status and color
        current_fps = fps_data.get('fps', 0)
        if current_fps >= 20:
            fps_color = colors['success']
            fps_status = "EXCELLENT"
        elif current_fps >= 15:
            fps_color = colors['warning']
            fps_status = "GOOD"
        elif current_fps >= 10:
            fps_color = (100, 180, 255)  # Light orange
            fps_status = "FAIR"
        else:
            fps_color = colors['danger']
            fps_status = "POOR"
        
        # FPS Gauge background
        cv2.rectangle(frame, (gauge_x, gauge_y), (gauge_x + gauge_width, gauge_y + gauge_height), colors['black'], -1)
        cv2.rectangle(frame, (gauge_x, gauge_y), (gauge_x + gauge_width, gauge_y + gauge_height), colors['secondary'], 2)
        
        # FPS Gauge fill
        max_fps = 30
        progress = min(current_fps / max_fps, 1.0)
        fill_width = int(gauge_width * progress)
        cv2.rectangle(frame, (gauge_x + 2, gauge_y + 2), (gauge_x + fill_width - 2, gauge_y + gauge_height - 2), fps_color, -1)
        
        # FPS Text
        fps_text = f"FPS: {current_fps:.1f} ({fps_status})"
        cv2.putText(frame, fps_text, (gauge_x + 10, gauge_y + 17), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors['white'], 1)
        
        # Performance metrics
        metrics_y = gauge_y + 45
        metrics = [
            f"Frame Time: {fps_data.get('frame_time', 0):.1f}ms",
            f"Users Loaded: {fps_data.get('users', 0)}",
            f"Cache Hits: {fps_data.get('cache_hits', 0)}",
            f"Memory: {fps_data.get('memory', 0):.1f}MB",
            f"Detection Count: {fps_data.get('faces', 0)}"
        ]
        
        for i, metric in enumerate(metrics):
            y_pos = metrics_y + i * 22
            cv2.putText(frame, metric, (panel_x + 15, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.45, colors['secondary'], 1)
        
        # 3. Control Panel (Bottom)
        control_height = 80
        control_y = height - control_height
        
        # Control panel background
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, control_y), (width, height), colors['dark'], -1)
        cv2.addWeighted(frame, 0.3, overlay, 0.7, 0, frame)
        
        # Control buttons
        if recognition_data:
            # Recognition mode controls
            controls = [
                ("Q - Quit", colors['danger']),
                ("R - Reset Cache", colors['warning']),
                ("S - Screenshot", colors['success'])
            ]
        else:
            # Registration mode controls
            controls = [
                ("S - Capture Sample", colors['success']),
                ("Q - Quit Registration", colors['danger']),
                ("Space - Skip Sample", colors['warning'])
            ]
        
        button_width = 180
        button_spacing = 20
        start_x = (width - (len(controls) * (button_width + button_spacing) - button_spacing)) // 2
        
        for i, (text, color) in enumerate(controls):
            button_x = start_x + i * (button_width + button_spacing)
            button_y = control_y + 15
            button_height = 35
            
            # Button background
            cv2.rectangle(frame, (button_x, button_y), (button_x + button_width, button_y + button_height), color, -1)
            cv2.rectangle(frame, (button_x, button_y), (button_x + button_width, button_y + button_height), colors['white'], 2)
            
            # Button text
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            text_x = button_x + (button_width - text_size[0]) // 2
            text_y = button_y + (button_height + text_size[1]) // 2
            cv2.putText(frame, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors['white'], 2)
        
        # 4. Mode indicator (Top right corner)
        mode = registration_data['mode'] if registration_data else 'RECOGNITION'
        mode_color = colors['warning'] if mode == 'REGISTRATION' else colors['success']
        cv2.putText(frame, f"MODE: {mode}", (width - 200, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, mode_color, 2)
        
        # 5. Registration specific UI
        if registration_data:
            # Progress indicator
            progress_text = f"Sample {registration_data['current']}/{registration_data['total']}"
            cv2.putText(frame, progress_text, (15, height - control_height - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, colors['primary'], 2)
            
            # User name
            user_text = f"Registering: {registration_data['name']}"
            cv2.putText(frame, user_text, (15, status_height + 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, colors['primary'], 2)
        
        # 6. Recognition specific UI
        if recognition_data and recognition_data.get('last_recognition'):
            # Last recognition result
            last_result = recognition_data['last_recognition']
            result_color = colors['success'] if last_result.get('is_match') else colors['danger']
            result_text = f"Last: {last_result.get('name', 'Unknown')} ({last_result.get('confidence', 0):.2f})"
            cv2.putText(frame, result_text, (15, status_height + 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, result_color, 2)
        
        return frame
    
    def _draw_face_overlay(self, frame, faces, results=None, mode='recognition'):
        """
        Yüz çerçeveleri ve etiketleri çizer.
        
        Args:
            frame: Video frame
            faces: Algılanan yüzler
            results: Tanıma sonuçları
            mode: Mod ('recognition' veya 'registration')
        """
        colors = {
            'success': (50, 205, 50),
            'danger': (50, 50, 255),
            'warning': (50, 180, 255),
            'primary': (240, 180, 50)
        }
        
        for i, (x, y, w, h) in enumerate(faces):
            if mode == 'registration':
                # Registration mode - simple green boxes
                color = colors['success']
                label = f"Face {i+1}"
                confidence_text = ""
            else:
                # Recognition mode
                if results and i < len(results):
                    result = results[i]
                    if result.is_match:
                        color = colors['success']
                        label = result.user_name
                        confidence_text = f" ({result.confidence:.2f})"
                    else:
                        color = colors['danger']
                        label = "Unknown"
                        confidence_text = f" ({result.confidence:.2f})"
                else:
                    color = colors['warning']
                    label = "Processing..."
                    confidence_text = ""
            
            # Enhanced face box with corners
            thickness = 3
            corner_length = 20
            
            # Main rectangle
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)
            
            # Corner accents
            # Top-left
            cv2.line(frame, (x, y), (x + corner_length, y), color, thickness + 2)
            cv2.line(frame, (x, y), (x, y + corner_length), color, thickness + 2)
            
            # Top-right
            cv2.line(frame, (x + w, y), (x + w - corner_length, y), color, thickness + 2)
            cv2.line(frame, (x + w, y), (x + w, y + corner_length), color, thickness + 2)
            
            # Bottom-left
            cv2.line(frame, (x, y + h), (x + corner_length, y + h), color, thickness + 2)
            cv2.line(frame, (x, y + h), (x, y + h - corner_length), color, thickness + 2)
            
            # Bottom-right
            cv2.line(frame, (x + w, y + h), (x + w - corner_length, y + h), color, thickness + 2)
            cv2.line(frame, (x + w, y + h), (x + w, y + h - corner_length), color, thickness + 2)
            
            # Label background
            label_text = f"{label}{confidence_text}"
            text_size = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            label_bg_x1 = x
            label_bg_y1 = y - 35
            label_bg_x2 = x + text_size[0] + 10
            label_bg_y2 = y - 5
            
            # Ensure label is within frame
            if label_bg_y1 < 0:
                label_bg_y1 = y + h + 5
                label_bg_y2 = y + h + 35
            
            cv2.rectangle(frame, (label_bg_x1, label_bg_y1), (label_bg_x2, label_bg_y2), color, -1)
            cv2.rectangle(frame, (label_bg_x1, label_bg_y1), (label_bg_x2, label_bg_y2), (255, 255, 255), 2)
            
            # Label text
            text_y = label_bg_y1 + 20 if label_bg_y1 > 0 else label_bg_y1 + 25
            cv2.putText(frame, label_text, (x + 5, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)


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