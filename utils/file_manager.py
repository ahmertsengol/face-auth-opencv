"""
Dosya yönetimi servisi - Dosya okuma, yazma ve path işlemleri
"""

import os
import json
import pickle
from pathlib import Path
from typing import Any, Optional, List, Dict
import shutil
from datetime import datetime
import re


class FileManager:
    """
    Dosya işlemlerinden sorumlu sınıf.
    Single Responsibility Principle: Sadece dosya işlemlerini yapar.
    """
    
    @staticmethod
    def ensure_directory(directory_path: str) -> bool:
        """
        Dizinin var olduğundan emin olur, yoksa oluşturur.
        
        Args:
            directory_path: Oluşturulacak dizin yolu
            
        Returns:
            Başarılı ise True, hata varsa False
        """
        try:
            Path(directory_path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Dizin oluşturulamadı: {e}")
            return False
    
    @staticmethod
    def save_json(data: Any, file_path: str) -> bool:
        """
        Veriyi JSON formatında kaydeder.
        
        Args:
            data: Kaydedilecek veri
            file_path: Dosya yolu
            
        Returns:
            Başarılı ise True, hata varsa False
        """
        try:
            # Dizinin var olduğundan emin ol
            FileManager.ensure_directory(os.path.dirname(file_path))
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
            
        except Exception as e:
            print(f"JSON kaydetme hatası: {e}")
            return False
    
    @staticmethod
    def load_json(file_path: str) -> Optional[Any]:
        """
        JSON dosyasını yükler.
        
        Args:
            file_path: Dosya yolu
            
        Returns:
            Yüklenen veri veya None
        """
        try:
            if not os.path.exists(file_path):
                return None
                
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            print(f"JSON yükleme hatası: {e}")
            return None
    
    @staticmethod
    def save_pickle(data: Any, file_path: str) -> bool:
        """
        Veriyi pickle formatında kaydeder.
        
        Args:
            data: Kaydedilecek veri
            file_path: Dosya yolu
            
        Returns:
            Başarılı ise True, hata varsa False
        """
        try:
            # Dizinin var olduğundan emin ol
            FileManager.ensure_directory(os.path.dirname(file_path))
            
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
            return True
            
        except Exception as e:
            print(f"Pickle kaydetme hatası: {e}")
            return False
    
    @staticmethod
    def load_pickle(file_path: str) -> Optional[Any]:
        """
        Pickle dosyasını yükler.
        
        Args:
            file_path: Dosya yolu
            
        Returns:
            Yüklenen veri veya None
        """
        try:
            if not os.path.exists(file_path):
                return None
                
            with open(file_path, 'rb') as f:
                return pickle.load(f)
                
        except Exception as e:
            print(f"Pickle yükleme hatası: {e}")
            return None
    
    @staticmethod
    def file_exists(file_path: str) -> bool:
        """
        Dosyanın var olup olmadığını kontrol eder.
        
        Args:
            file_path: Kontrol edilecek dosya yolu
            
        Returns:
            Varsa True, yoksa False
        """
        return os.path.exists(file_path) and os.path.isfile(file_path)
    
    @staticmethod
    def directory_exists(directory_path: str) -> bool:
        """
        Dizinin var olup olmadığını kontrol eder.
        
        Args:
            directory_path: Kontrol edilecek dizin yolu
            
        Returns:
            Varsa True, yoksa False
        """
        return os.path.exists(directory_path) and os.path.isdir(directory_path)
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """
        Dosyayı siler.
        
        Args:
            file_path: Silinecek dosya yolu
            
        Returns:
            Başarılı ise True, hata varsa False
        """
        try:
            if FileManager.file_exists(file_path):
                os.remove(file_path)
                return True
            else:
                print(f"Dosya bulunamadı: {file_path}")
                return False
                
        except Exception as e:
            print(f"Dosya silme hatası: {e}")
            return False
    
    @staticmethod
    def delete_directory(directory_path: str) -> bool:
        """
        Dizini ve içeriğini siler.
        
        Args:
            directory_path: Silinecek dizin yolu
            
        Returns:
            Başarılı ise True, hata varsa False
        """
        try:
            if FileManager.directory_exists(directory_path):
                shutil.rmtree(directory_path)
                return True
            else:
                print(f"Dizin bulunamadı: {directory_path}")
                return False
                
        except Exception as e:
            print(f"Dizin silme hatası: {e}")
            return False
    
    @staticmethod
    def copy_file(source_path: str, destination_path: str) -> bool:
        """
        Dosyayı kopyalar.
        
        Args:
            source_path: Kaynak dosya yolu
            destination_path: Hedef dosya yolu
            
        Returns:
            Başarılı ise True, hata varsa False
        """
        try:
            if not FileManager.file_exists(source_path):
                print(f"Kaynak dosya bulunamadı: {source_path}")
                return False
            
            # Hedef dizini oluştur
            FileManager.ensure_directory(os.path.dirname(destination_path))
            
            shutil.copy2(source_path, destination_path)
            return True
            
        except Exception as e:
            print(f"Dosya kopyalama hatası: {e}")
            return False
    
    @staticmethod
    def move_file(source_path: str, destination_path: str) -> bool:
        """
        Dosyayı taşır.
        
        Args:
            source_path: Kaynak dosya yolu
            destination_path: Hedef dosya yolu
            
        Returns:
            Başarılı ise True, hata varsa False
        """
        try:
            if not FileManager.file_exists(source_path):
                print(f"Kaynak dosya bulunamadı: {source_path}")
                return False
            
            # Hedef dizini oluştur
            FileManager.ensure_directory(os.path.dirname(destination_path))
            
            shutil.move(source_path, destination_path)
            return True
            
        except Exception as e:
            print(f"Dosya taşıma hatası: {e}")
            return False
    
    @staticmethod
    def get_file_size(file_path: str) -> Optional[int]:
        """
        Dosya boyutunu döndürür.
        
        Args:
            file_path: Dosya yolu
            
        Returns:
            Dosya boyutu (byte) veya None
        """
        try:
            if FileManager.file_exists(file_path):
                return os.path.getsize(file_path)
            return None
            
        except Exception as e:
            print(f"Dosya boyutu alma hatası: {e}")
            return None
    
    @staticmethod
    def get_file_modification_time(file_path: str) -> Optional[datetime]:
        """
        Dosya değiştirilme zamanını döndürür.
        
        Args:
            file_path: Dosya yolu
            
        Returns:
            Değiştirilme zamanı veya None
        """
        try:
            if FileManager.file_exists(file_path):
                timestamp = os.path.getmtime(file_path)
                return datetime.fromtimestamp(timestamp)
            return None
            
        except Exception as e:
            print(f"Dosya zamanı alma hatası: {e}")
            return None
    
    @staticmethod
    def list_files_in_directory(directory_path: str, extension: Optional[str] = None) -> List[str]:
        """
        Dizindeki dosyaları listeler.
        
        Args:
            directory_path: Dizin yolu
            extension: Filtrelenecek dosya uzantısı (opsiyonel)
            
        Returns:
            Dosya isimlerinin listesi
        """
        try:
            if not FileManager.directory_exists(directory_path):
                return []
            
            files = []
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                if os.path.isfile(item_path):
                    if extension is None or item.endswith(extension):
                        files.append(item)
            
            return sorted(files)
            
        except Exception as e:
            print(f"Dizin listeleme hatası: {e}")
            return []
    
    @staticmethod
    def get_safe_filename(filename: str) -> str:
        """
        Dosya adını güvenli hale getirir.
        Özel karakterleri temizler ve path traversal saldırılarını önler.
        
        Args:
            filename: Düzenlenecek dosya adı
            
        Returns:
            Güvenli dosya adı
        """
        # Zararlı karakterleri temizle
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Path traversal saldırılarını önle
        safe_filename = safe_filename.replace('..', '_')
        
        # Boş değilse geri döndür
        return safe_filename if safe_filename.strip() else 'unnamed_file'
    
    @staticmethod
    def is_safe_path(file_path: str, allowed_dirs: List[str] = None) -> bool:
        """
        Dosya yolunun güvenli olup olmadığını kontrol eder.
        Path traversal saldırılarını önler.
        
        Args:
            file_path: Kontrol edilecek dosya yolu
            allowed_dirs: İzin verilen dizinler listesi
            
        Returns:
            Güvenli ise True, değilse False
        """
        try:
            # Absolute path'e çevir
            abs_path = os.path.abspath(file_path)
            
            # Path traversal kontrolü (file_path'te, abs_path'te değil)
            if '..' in os.path.normpath(file_path) or file_path.startswith('~'):
                return False
            
            # Proje dizini kontrolü
            project_root = os.path.abspath('.')
            
            # Güvenli dizinler
            safe_dirs = [
                project_root,
                '/tmp',
                '/var/tmp',
                '/var/folders'  # macOS temp folders
            ]
            
            if allowed_dirs:
                safe_dirs.extend([os.path.abspath(d) for d in allowed_dirs])
            
            # Herhangi bir güvenli dizin altında mı kontrol et
            for safe_dir in safe_dirs:
                if abs_path.startswith(safe_dir):
                    return True
            
            return False
            
        except Exception:
            return False
    
    @staticmethod
    def read_file(file_path: str) -> Optional[str]:
        """
        Dosya içeriğini güvenli şekilde okur.
        
        Args:
            file_path: Okunacak dosya yolu
            
        Returns:
            Dosya içeriği veya None
        """
        try:
            # Güvenlik kontrolü
            if not FileManager.is_safe_path(file_path):
                print(f"Güvensiz dosya yolu: {file_path}")
                return None
            
            if not FileManager.file_exists(file_path):
                return None
                
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
                
        except Exception as e:
            print(f"Dosya okuma hatası: {e}")
            return None
    
    @staticmethod
    def write_file(file_path: str, content: str) -> bool:
        """
        Dosyaya güvenli şekilde yazar.
        
        Args:
            file_path: Yazılacak dosya yolu
            content: Yazılacak içerik
            
        Returns:
            Başarılı ise True, hata varsa False
        """
        try:
            # Güvenlik kontrolü
            if not FileManager.is_safe_path(file_path):
                print(f"Güvensiz dosya yolu: {file_path}")
                return False
            
            # Dizinin var olduğundan emin ol
            FileManager.ensure_directory(os.path.dirname(file_path))
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
            
        except Exception as e:
            print(f"Dosya yazma hatası: {e}")
            return False 