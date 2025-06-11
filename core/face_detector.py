"""
Yüz algılama servisi - Görüntülerde yüz tespiti yapar
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
import face_recognition
import threading
import time
from functools import lru_cache
import gc


class OptimizedFaceDetector:
    """
    Optimize edilmiş yüz algılama sınıfı.
    Performance: Threading, caching, memory management
    """
    
    def __init__(self, max_workers: int = 2) -> None:
        """FaceDetector sınıfını başlatır."""
        self._cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self._face_cascade = cv2.CascadeClassifier(self._cascade_path)
        
        if self._face_cascade.empty():
            raise RuntimeError("Yüz algılama modeli yüklenemedi!")
        
        # Performance settings
        self._max_workers = max_workers
        self._detection_cache: Dict[str, Any] = {}
        self._cache_timeout = 5.0  # seconds
        self._last_cleanup = time.time()
        
        # Threading lock
        self._lock = threading.Lock()
        
        # Optimization parameters
        self._opencv_params = {
            'scaleFactor': 1.1,
            'minNeighbors': 3,  # Reduced for speed
            'minSize': (50, 50),  # Increased for performance
            'flags': cv2.CASCADE_SCALE_IMAGE
        }
    
    def _cleanup_cache(self) -> None:
        """Cache temizliği yapar."""
        current_time = time.time()
        if current_time - self._last_cleanup > self._cache_timeout:
            with self._lock:
                self._detection_cache.clear()
                self._last_cleanup = current_time
                gc.collect()  # Memory cleanup
    
    def _get_frame_hash(self, frame: np.ndarray) -> str:
        """Frame için hash oluşturur (caching için)."""
        # Küçük bir sample alıp hash oluştur (performans için)
        h, w = frame.shape[:2]
        sample = frame[h//4:3*h//4, w//4:3*w//4]
        return str(hash(sample.tobytes()))
    
    @lru_cache(maxsize=128)
    def _get_gray_frame(self, frame_hash: str, frame_data: bytes) -> np.ndarray:
        """Gri frame'i cache'li olarak döndürür."""
        frame = np.frombuffer(frame_data, dtype=np.uint8)
        frame = frame.reshape((-1, frame.shape[-1]//3, 3))
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    def detect_faces_opencv_optimized(self, frame: np.ndarray, use_cache: bool = True) -> List[Tuple[int, int, int, int]]:
        """
        Optimize edilmiş OpenCV yüz algılama.
        
        Args:
            frame: Algılanacak görüntü frame'i
            use_cache: Cache kullanımı
            
        Returns:
            Algılanan yüzlerin koordinat listesi [(x, y, w, h), ...]
        """
        if frame is None or frame.size == 0:
            return []
        
        # Cache kontrolü
        frame_hash = self._get_frame_hash(frame) if use_cache else None
        if use_cache and frame_hash in self._detection_cache:
            cache_data = self._detection_cache[frame_hash]
            if time.time() - cache_data['timestamp'] < self._cache_timeout:
                return cache_data['faces']
        
        # Cleanup check
        self._cleanup_cache()
        
        # Frame'i optimize et
        height, width = frame.shape[:2]
        if width > 640:  # Resize for performance
            scale = 640 / width
            new_width, new_height = int(width * scale), int(height * scale)
            frame = cv2.resize(frame, (new_width, new_height))
            scale_factor = 1 / scale
        else:
            scale_factor = 1.0
        
        # Gri frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Histogram equalization for better detection
        gray = cv2.equalizeHist(gray)
        
        # Yüz algılama
        faces = self._face_cascade.detectMultiScale(gray, **self._opencv_params)
        
        # Scale back if resized
        if scale_factor != 1.0:
            faces = [(int(x * scale_factor), int(y * scale_factor), 
                     int(w * scale_factor), int(h * scale_factor)) 
                    for x, y, w, h in faces]
        else:
            faces = [(int(x), int(y), int(w), int(h)) for x, y, w, h in faces]
        
        # Cache'e kaydet
        if use_cache and frame_hash:
            with self._lock:
                self._detection_cache[frame_hash] = {
                    'faces': faces,
                    'timestamp': time.time()
                }
        
        return faces
    
    def detect_faces_dlib_optimized(self, frame: np.ndarray, model: str = "hog") -> List[Tuple[int, int, int, int]]:
        """
        Optimize edilmiş dlib yüz algılama.
        
        Args:
            frame: Algılanacak görüntü frame'i
            model: "hog" (fast) or "cnn" (accurate)
            
        Returns:
            Algılanan yüzlerin koordinat listesi [(x, y, w, h), ...]
        """
        if frame is None or frame.size == 0:
            return []
        
        # Frame boyutunu optimize et
        height, width = frame.shape[:2]
        if width > 480:  # dlib için daha küçük
            scale = 480 / width
            new_width, new_height = int(width * scale), int(height * scale)
            frame = cv2.resize(frame, (new_width, new_height))
            scale_factor = 1 / scale
        else:
            scale_factor = 1.0
            
        # RGB formatına çevir (face_recognition RGB bekler)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Yüz lokasyonlarını bul
        face_locations = face_recognition.face_locations(rgb_frame, model=model)
        
        # (top, right, bottom, left) formatından (x, y, w, h) formatına çevir
        faces = []
        for top, right, bottom, left in face_locations:
            x, y = left, top
            w, h = right - left, bottom - top
            
            # Scale back if resized
            if scale_factor != 1.0:
                x, y, w, h = int(x * scale_factor), int(y * scale_factor), int(w * scale_factor), int(h * scale_factor)
            
            faces.append((x, y, w, h))
            
        return faces
    
    def get_face_encodings_optimized(self, frame: np.ndarray, known_face_locations: Optional[List] = None) -> List[np.ndarray]:
        """
        Optimize edilmiş yüz encoding çıkarma.
        
        Args:
            frame: Encoding çıkarılacak görüntü frame'i
            known_face_locations: Bilinen yüz konumları (performans için)
            
        Returns:
            Yüz encoding'lerinin listesi
        """
        if frame is None or frame.size == 0:
            return []
        
        # Frame boyutunu optimize et
        height, width = frame.shape[:2]
        if width > 640:
            scale = 640 / width
            new_width, new_height = int(width * scale), int(height * scale)
            frame = cv2.resize(frame, (new_width, new_height))
            
            # Known locations'ı da scale et
            if known_face_locations:
                known_face_locations = [
                    (int(top * scale), int(right * scale), int(bottom * scale), int(left * scale))
                    for top, right, bottom, left in known_face_locations
                ]
            
        # RGB formatına çevir
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Eğer locations verilmemişse, önce algıla
        if known_face_locations is None:
            face_locations = face_recognition.face_locations(rgb_frame, model="hog")  # Fast model
        else:
            face_locations = known_face_locations
        
        # Encoding'leri çıkar (num_jitters=1 for speed)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations, num_jitters=1)
        
        return face_encodings
    
    def extract_face_region(self, frame: np.ndarray, face_coords: Tuple[int, int, int, int], padding: int = 10) -> Optional[np.ndarray]:
        """
        Optimize edilmiş yüz bölgesi çıkarma.
        
        Args:
            frame: Kaynak görüntü
            face_coords: Yüz koordinatları (x, y, w, h)
            padding: Kenar padding'i
            
        Returns:
            Çıkarılan yüz bölgesi veya None
        """
        if frame is None or frame.size == 0:
            return None
            
        x, y, w, h = face_coords
        
        # Padding ekle
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = w + 2 * padding
        h = h + 2 * padding
        
        # Sınırları kontrol et
        height, width = frame.shape[:2]
        if x < 0 or y < 0 or x + w > width or y + h > height:
            # Sınırları düzelt
            x = max(0, x)
            y = max(0, y)
            w = min(w, width - x)
            h = min(h, height - y)
            
        if w <= 0 or h <= 0:
            return None
            
        return frame[y:y+h, x:x+w]
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Performance istatistiklerini döndürür."""
        with self._lock:
            return {
                'cache_size': len(self._detection_cache),
                'cache_timeout': self._cache_timeout,
                'max_workers': self._max_workers,
                'last_cleanup': self._last_cleanup
            }
    
    def clear_cache(self) -> None:
        """Cache'i temizler."""
        with self._lock:
            self._detection_cache.clear()
            gc.collect()


# Backward compatibility
class FaceDetector(OptimizedFaceDetector):
    """Backward compatibility için alias."""
    
    def detect_faces_opencv(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        return self.detect_faces_opencv_optimized(frame)
    
    def detect_faces_dlib(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        return self.detect_faces_dlib_optimized(frame)
    
    def get_face_encodings(self, frame: np.ndarray) -> List[np.ndarray]:
        return self.get_face_encodings_optimized(frame)
    
    def detect_and_encode(self, image_data: bytes) -> List[np.ndarray]:
        """
        Byte veriden yüz algılama ve encoding çıkarma.
        
        Args:
            image_data: Görüntü byte verisi
            
        Returns:
            Yüz encoding'lerinin listesi
        """
        try:
            # Byte veriden numpy array oluştur
            nparr = np.frombuffer(image_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                return []
            
            return self.detect_and_encode_cv2(frame)
        except Exception as e:
            print(f"Error in detect_and_encode: {e}")
            return []
    
    def detect_and_encode_cv2(self, frame: np.ndarray) -> List[np.ndarray]:
        """
        OpenCV frame'den yüz algılama ve encoding çıkarma.
        
        Args:
            frame: OpenCV frame (BGR format)
            
        Returns:
            Yüz encoding'lerinin listesi
        """
        try:
            # RGB formatına çevir (face_recognition RGB bekler)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Yüz encoding'lerini çıkar
            return self.get_face_encodings_optimized(rgb_frame)
        except Exception as e:
            print(f"Error in detect_and_encode_cv2: {e}")
            return [] 