"""
Yüz algılama servisi - Görüntülerde yüz tespiti yapar
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional
import face_recognition


class FaceDetector:
    """
    Yüz algılama işlemlerinden sorumlu sınıf.
    Single Responsibility Principle: Sadece yüz algılama işlemlerini yapar.
    """
    
    def __init__(self) -> None:
        """FaceDetector sınıfını başlatır."""
        self._cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self._face_cascade = cv2.CascadeClassifier(self._cascade_path)
        
        if self._face_cascade.empty():
            raise RuntimeError("Yüz algılama modeli yüklenemedi!")
    
    def detect_faces_opencv(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        OpenCV kullanarak yüzleri algılar (hızlı ama daha az doğru).
        
        Args:
            frame: Algılanacak görüntü frame'i
            
        Returns:
            Algılanan yüzlerin koordinat listesi [(x, y, w, h), ...]
        """
        if frame is None or frame.size == 0:
            return []
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self._face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        return [(int(x), int(y), int(w), int(h)) for x, y, w, h in faces]
    
    def detect_faces_dlib(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        face_recognition (dlib) kullanarak yüzleri algılar (yavaş ama daha doğru).
        
        Args:
            frame: Algılanacak görüntü frame'i
            
        Returns:
            Algılanan yüzlerin koordinat listesi [(x, y, w, h), ...]
        """
        if frame is None or frame.size == 0:
            return []
            
        # RGB formatına çevir (face_recognition RGB bekler)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Yüz lokasyonlarını bul
        face_locations = face_recognition.face_locations(rgb_frame)
        
        # (top, right, bottom, left) formatından (x, y, w, h) formatına çevir
        faces = []
        for top, right, bottom, left in face_locations:
            x, y = left, top
            w, h = right - left, bottom - top
            faces.append((x, y, w, h))
            
        return faces
    
    def get_face_encodings(self, frame: np.ndarray) -> List[np.ndarray]:
        """
        Görüntüdeki yüzlerin encoding'lerini (özellik vektörlerini) çıkarır.
        
        Args:
            frame: Encoding çıkarılacak görüntü frame'i
            
        Returns:
            Yüz encoding'lerinin listesi
        """
        if frame is None or frame.size == 0:
            return []
            
        # RGB formatına çevir
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Yüz lokasyonlarını bul
        face_locations = face_recognition.face_locations(rgb_frame)
        
        # Yüz encoding'lerini çıkar
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        return face_encodings
    
    def extract_face_region(self, frame: np.ndarray, face_coords: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        """
        Verilen koordinatlara göre yüz bölgesini çıkarır.
        
        Args:
            frame: Kaynak görüntü
            face_coords: Yüz koordinatları (x, y, w, h)
            
        Returns:
            Çıkarılan yüz bölgesi veya None
        """
        if frame is None or frame.size == 0:
            return None
            
        x, y, w, h = face_coords
        
        # Sınırları kontrol et
        height, width = frame.shape[:2]
        if x < 0 or y < 0 or x + w > width or y + h > height:
            return None
            
        return frame[y:y+h, x:x+w] 