"""
Kamera yönetimi servisi - Kamera erişimi ve video frame yakalama
"""

import cv2
import numpy as np
from typing import Optional, Tuple
import time


class CameraManager:
    """
    Kamera yönetiminden sorumlu sınıf.
    Single Responsibility Principle: Sadece kamera işlemlerini yapar.
    """
    
    def __init__(self, camera_index: int = 0) -> None:
        """
        CameraManager sınıfını başlatır.
        
        Args:
            camera_index: Kullanılacak kamera indeksi (varsayılan: 0)
        """
        self._camera_index = camera_index
        self._capture: Optional[cv2.VideoCapture] = None
        self._is_initialized = False
        
    def initialize(self) -> bool:
        """
        Kamerayı başlatır.
        
        Returns:
            Başarılı ise True, hata varsa False
        """
        try:
            self._capture = cv2.VideoCapture(self._camera_index)
            
            if not self._capture.isOpened():
                print(f"Kamera açılamadı (index: {self._camera_index})")
                return False
            
            # Kamera ayarlarını optimize et
            self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self._capture.set(cv2.CAP_PROP_FPS, 30)
            
            self._is_initialized = True
            print(f"Kamera başarıyla başlatıldı (index: {self._camera_index})")
            return True
            
        except Exception as e:
            print(f"Kamera başlatılırken hata: {e}")
            return False
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Kameradan bir frame yakalar.
        
        Returns:
            Yakalanan frame veya None
        """
        if not self._is_initialized or self._capture is None:
            print("Kamera başlatılmamış!")
            return None
        
        try:
            ret, frame = self._capture.read()
            
            if not ret or frame is None:
                print("Frame yakalanamadı!")
                return None
                
            return frame
            
        except Exception as e:
            print(f"Frame yakalama hatası: {e}")
            return None
    
    def capture_multiple_frames(self, count: int, delay: float = 0.5) -> list[np.ndarray]:
        """
        Birden fazla frame yakalar.
        
        Args:
            count: Yakalanacak frame sayısı
            delay: Frame'ler arası bekleme süresi (saniye)
            
        Returns:
            Yakalanan frame'lerin listesi
        """
        frames = []
        
        for i in range(count):
            frame = self.capture_frame()
            if frame is not None:
                frames.append(frame)
                print(f"Frame {i+1}/{count} yakalandı")
                
                if i < count - 1:  # Son frame'de bekleme
                    time.sleep(delay)
            else:
                print(f"Frame {i+1} yakalanamadı!")
                
        return frames
    
    def is_camera_available(self) -> bool:
        """
        Kameranın kullanılabilir olup olmadığını kontrol eder.
        
        Returns:
            Kamera kullanılabilir ise True, değilse False
        """
        return self._is_initialized and self._capture is not None and self._capture.isOpened()
    
    def get_camera_info(self) -> dict:
        """
        Kamera bilgilerini döndürür.
        
        Returns:
            Kamera bilgileri dictionary'si
        """
        if not self.is_camera_available():
            return {"status": "Kamera kullanılamıyor"}
        
        try:
            width = int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(self._capture.get(cv2.CAP_PROP_FPS))
            
            return {
                "status": "Aktif",
                "index": self._camera_index,
                "resolution": f"{width}x{height}",
                "fps": fps,
                "width": width,
                "height": height
            }
            
        except Exception as e:
            return {"status": f"Bilgi alınamadı: {e}"}
    
    def set_resolution(self, width: int, height: int) -> bool:
        """
        Kamera çözünürlüğünü ayarlar.
        
        Args:
            width: Genişlik
            height: Yükseklik
            
        Returns:
            Başarılı ise True, hata varsa False
        """
        if not self.is_camera_available():
            return False
        
        try:
            self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
            # Ayarların uygulanıp uygulanmadığını kontrol et
            actual_width = int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            print(f"Çözünürlük ayarlandı: {actual_width}x{actual_height}")
            return True
            
        except Exception as e:
            print(f"Çözünürlük ayarlama hatası: {e}")
            return False
    
    def release(self) -> None:
        """Kamera kaynaklarını serbest bırakır."""
        try:
            if self._capture is not None:
                self._capture.release()
                print("Kamera kaynakları serbest bırakıldı")
                
            self._is_initialized = False
            self._capture = None
            
        except Exception as e:
            print(f"Kamera kapatma hatası: {e}")
    
    def __enter__(self):
        """Context manager desteği."""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager desteği."""
        self.release()
    
    def test_camera(self) -> bool:
        """
        Kamera testini yapar.
        
        Returns:
            Test başarılı ise True, hata varsa False
        """
        print("Kamera testi başlatılıyor...")
        
        if not self.initialize():
            return False
        
        # Test frame yakala
        test_frame = self.capture_frame()
        
        if test_frame is not None:
            print(f"Test başarılı! Frame boyutu: {test_frame.shape}")
            return True
        else:
            print("Test başarısız! Frame yakalanamadı.")
            return False 