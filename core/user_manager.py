"""
Kullanıcı yönetimi servisi - Kullanıcı verilerini kaydetme ve yükleme
"""

import os
import pickle
import json
import numpy as np
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class UserData:
    """Kullanıcı veri sınıfı."""
    name: str
    face_encodings: List[np.ndarray]
    created_at: str
    updated_at: str


class UserManager:
    """
    Kullanıcı veri yönetiminden sorumlu sınıf.
    Single Responsibility Principle: Sadece kullanıcı verilerini yönetir.
    """
    
    def __init__(self, data_dir: str = "data/users") -> None:
        """
        UserManager sınıfını başlatır.
        
        Args:
            data_dir: Kullanıcı verilerinin saklanacağı dizin
        """
        self._data_dir = Path(data_dir)
        self._ensure_data_directory()
    
    def _ensure_data_directory(self) -> None:
        """Veri dizininin var olduğundan emin olur."""
        self._data_dir.mkdir(parents=True, exist_ok=True)
    
    def save_user(self, user_data: UserData) -> bool:
        """
        Kullanıcı verilerini dosyaya kaydeder.
        
        Args:
            user_data: Kaydedilecek kullanıcı verisi
            
        Returns:
            Başarılı ise True, hata varsa False
        """
        try:
            if not user_data.name or not user_data.name.strip():
                raise ValueError("Geçersiz kullanıcı adı")
                
            file_path = self._get_user_file_path(user_data.name)
            
            # Face encodings'leri serialize edilebilir hale getir
            serializable_data = {
                'name': user_data.name,
                'face_encodings': [encoding.tolist() for encoding in user_data.face_encodings],
                'created_at': user_data.created_at,
                'updated_at': user_data.updated_at
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            print(f"Kullanıcı kaydedilemedi: {e}")
            return False
    
    def load_user(self, name: str) -> Optional[UserData]:
        """
        Kullanıcı verilerini dosyadan yükler.
        
        Args:
            name: Yüklenecek kullanıcının adı
            
        Returns:
            Kullanıcı verisi veya None
        """
        try:
            if not name or not name.strip():
                return None
                
            file_path = self._get_user_file_path(name)
            
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Face encodings'leri numpy array'e çevir
            face_encodings = [np.array(encoding) for encoding in data['face_encodings']]
            
            return UserData(
                name=data['name'],
                face_encodings=face_encodings,
                created_at=data['created_at'],
                updated_at=data['updated_at']
            )
            
        except Exception as e:
            print(f"Kullanıcı yüklenemedi: {e}")
            return None
    
    def load_all_users(self) -> List[UserData]:
        """
        Tüm kullanıcı verilerini yükler.
        
        Returns:
            Kullanıcı verilerinin listesi
        """
        users = []
        
        try:
            for file_path in self._data_dir.glob("*.json"):
                name = file_path.stem
                user_data = self.load_user(name)
                if user_data:
                    users.append(user_data)
                    
        except Exception as e:
            print(f"Kullanıcılar yüklenirken hata: {e}")
            
        return users
    
    def delete_user(self, name: str) -> bool:
        """
        Kullanıcı verilerini siler.
        
        Args:
            name: Silinecek kullanıcının adı
            
        Returns:
            Başarılı ise True, hata varsa False
        """
        try:
            if not name or not name.strip():
                return False
                
            file_path = self._get_user_file_path(name)
            
            if file_path.exists():
                file_path.unlink()
                return True
            else:
                print(f"Kullanıcı bulunamadı: {name}")
                return False
                
        except Exception as e:
            print(f"Kullanıcı silinemedi: {e}")
            return False
    
    def user_exists(self, name: str) -> bool:
        """
        Kullanıcının var olup olmadığını kontrol eder.
        
        Args:
            name: Kontrol edilecek kullanıcının adı
            
        Returns:
            Varsa True, yoksa False
        """
        if not name or not name.strip():
            return False
            
        file_path = self._get_user_file_path(name)
        return file_path.exists()
    
    def get_user_count(self) -> int:
        """Toplam kullanıcı sayısını döndürür."""
        try:
            return len(list(self._data_dir.glob("*.json")))
        except Exception:
            return 0
    
    def get_user_names(self) -> List[str]:
        """Tüm kullanıcı isimlerini döndürür."""
        try:
            return [file_path.stem for file_path in self._data_dir.glob("*.json")]
        except Exception:
            return []
    
    def _get_user_file_path(self, name: str) -> Path:
        """
        Kullanıcı dosya yolunu oluşturur.
        
        Args:
            name: Kullanıcı adı
            
        Returns:
            Dosya yolu
        """
        # Dosya adında kullanılamayacak karakterleri temizle
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
        return self._data_dir / f"{safe_name}.json"
    
    def backup_all_users(self, backup_path: str) -> bool:
        """
        Tüm kullanıcı verilerini yedekler.
        
        Args:
            backup_path: Yedek dosyasının yolu
            
        Returns:
            Başarılı ise True, hata varsa False
        """
        try:
            all_users = self.load_all_users()
            
            backup_data = []
            for user in all_users:
                backup_data.append({
                    'name': user.name,
                    'face_encodings': [encoding.tolist() for encoding in user.face_encodings],
                    'created_at': user.created_at,
                    'updated_at': user.updated_at
                })
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            print(f"Yedekleme başarısız: {e}")
            return False 