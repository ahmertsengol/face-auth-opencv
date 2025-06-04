"""
Yüz tanıma servisi - Kayıtlı yüzlerle karşılaştırma yapar
"""

import numpy as np
import face_recognition
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass


@dataclass
class RecognitionResult:
    """Tanıma sonucu için veri sınıfı."""
    user_name: str
    confidence: float
    is_match: bool


class FaceRecognizer:
    """
    Yüz tanıma işlemlerinden sorumlu sınıf.
    Single Responsibility Principle: Sadece yüz tanıma işlemlerini yapar.
    """
    
    def __init__(self, tolerance: float = 0.6) -> None:
        """
        FaceRecognizer sınıfını başlatır.
        
        Args:
            tolerance: Yüz eşleştirme toleransı (düşük = katı, yüksek = esnek)
        """
        self._tolerance = tolerance
        self._known_face_encodings: List[np.ndarray] = []
        self._known_face_names: List[str] = []
    
    def add_known_face(self, face_encoding: np.ndarray, name: str) -> None:
        """
        Bilinen yüzler listesine yeni bir yüz ekler.
        
        Args:
            face_encoding: Yüzün encoding verisi
            name: Yüzün sahibinin adı
        """
        if face_encoding is None or len(face_encoding) == 0:
            raise ValueError("Geçersiz face encoding")
            
        if not name or not name.strip():
            raise ValueError("Geçersiz isim")
            
        self._known_face_encodings.append(face_encoding)
        self._known_face_names.append(name.strip())
    
    def clear_known_faces(self) -> None:
        """Bilinen yüzler listesini temizler."""
        self._known_face_encodings.clear()
        self._known_face_names.clear()
    
    def recognize_faces(self, face_encodings: List[np.ndarray]) -> List[RecognitionResult]:
        """
        Verilen yüz encoding'lerini bilinen yüzlerle karşılaştırır.
        
        Args:
            face_encodings: Tanınacak yüzlerin encoding'leri
            
        Returns:
            Tanıma sonuçlarının listesi
        """
        if not face_encodings:
            return []
            
        if not self._known_face_encodings:
            return [RecognitionResult("Bilinmeyen", 0.0, False) for _ in face_encodings]
        
        results = []
        
        for face_encoding in face_encodings:
            result = self._recognize_single_face(face_encoding)
            results.append(result)
            
        return results
    
    def _recognize_single_face(self, face_encoding: np.ndarray) -> RecognitionResult:
        """
        Tek bir yüz encoding'ini tanır.
        
        Args:
            face_encoding: Tanınacak yüzün encoding'i
            
        Returns:
            Tanıma sonucu
        """
        if face_encoding is None or len(face_encoding) == 0:
            return RecognitionResult("Geçersiz", 0.0, False)
        
        # Tüm bilinen yüzlerle karşılaştır
        face_distances = face_recognition.face_distance(self._known_face_encodings, face_encoding)
        
        # En yakın eşleşmeyi bul
        best_match_index = np.argmin(face_distances)
        best_distance = face_distances[best_match_index]
        
        # Eşleşme kontrolü
        is_match = best_distance <= self._tolerance
        confidence = max(0.0, 1.0 - best_distance)  # Mesafeyi güven skoruna çevir
        
        if is_match:
            name = self._known_face_names[best_match_index]
            return RecognitionResult(name, confidence, True)
        else:
            return RecognitionResult("Bilinmeyen", confidence, False)
    
    def get_known_faces_count(self) -> int:
        """Kayıtlı yüz sayısını döndürür."""
        return len(self._known_face_encodings)
    
    def get_known_names(self) -> List[str]:
        """Kayıtlı isimlerin listesini döndürür."""
        return self._known_face_names.copy()
    
    def remove_known_face(self, name: str) -> bool:
        """
        Belirtilen isimli yüzü bilinen yüzler listesinden kaldırır.
        
        Args:
            name: Kaldırılacak yüzün sahibinin adı
            
        Returns:
            Başarılı ise True, bulunamadı ise False
        """
        try:
            index = self._known_face_names.index(name)
            self._known_face_encodings.pop(index)
            self._known_face_names.pop(index)
            return True
        except ValueError:
            return False
    
    def update_tolerance(self, new_tolerance: float) -> None:
        """
        Tanıma toleransını günceller.
        
        Args:
            new_tolerance: Yeni tolerans değeri (0.0 - 1.0 arası)
        """
        if not 0.0 <= new_tolerance <= 1.0:
            raise ValueError("Tolerans 0.0 ile 1.0 arasında olmalıdır")
            
        self._tolerance = new_tolerance
    
    def get_tolerance(self) -> float:
        """Mevcut tolerans değerini döndürür."""
        return self._tolerance 