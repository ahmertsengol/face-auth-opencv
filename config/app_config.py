"""
Merkezi konfigürasyon yönetimi sistemi
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import logging


@dataclass
class CameraConfig:
    """Kamera konfigürasyonu."""
    index: int = 0
    width: int = 640
    height: int = 480
    fps: int = 30


@dataclass
class DetectionConfig:
    """Yüz algılama konfigürasyonu."""
    opencv_scale_factor: float = 1.1
    opencv_min_neighbors: int = 3
    opencv_min_size: tuple = (50, 50)
    dlib_model: str = "hog"  # "hog" or "cnn"
    face_encoding_jitters: int = 1
    recognition_tolerance: float = 0.6
    cache_timeout: float = 5.0
    max_cache_size: int = 128


@dataclass
class SystemConfig:
    """Sistem konfigürasyonu."""
    data_dir: str = "data/users"
    logs_dir: str = "logs"
    backup_dir: str = "data/backups"
    max_workers: int = 2
    auto_cleanup: bool = True
    log_level: str = "INFO"


@dataclass
class UIConfig:
    """Kullanıcı arayüzü konfigürasyonu."""
    window_width: int = 800
    window_height: int = 600
    show_fps: bool = True
    show_confidence: bool = True
    success_color: tuple = (0, 255, 0)
    error_color: tuple = (0, 0, 255)
    text_color: tuple = (255, 255, 255)


@dataclass
class AppConfig:
    """Ana uygulama konfigürasyonu."""
    camera: CameraConfig
    detection: DetectionConfig
    system: SystemConfig
    ui: UIConfig
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'AppConfig':
        """Dictionary'den AppConfig oluşturur."""
        return cls(
            camera=CameraConfig(**config_dict.get('camera', {})),
            detection=DetectionConfig(**config_dict.get('detection', {})),
            system=SystemConfig(**config_dict.get('system', {})),
            ui=UIConfig(**config_dict.get('ui', {}))
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """AppConfig'i dictionary'e çevirir."""
        return {
            'camera': asdict(self.camera),
            'detection': asdict(self.detection),
            'system': asdict(self.system),
            'ui': asdict(self.ui)
        }


class ConfigManager:
    """
    Konfigürasyon yönetimi sınıfı.
    """
    
    def __init__(self, config_path: str = "config/app_config.json"):
        """ConfigManager başlatır."""
        self.config_path = Path(config_path)
        self.config: AppConfig = self._load_config()
    
    def _get_default_config(self) -> AppConfig:
        """Varsayılan konfigürasyon döndürür."""
        return AppConfig(
            camera=CameraConfig(),
            detection=DetectionConfig(),
            system=SystemConfig(),
            ui=UIConfig()
        )
    
    def _load_config(self) -> AppConfig:
        """Konfigürasyonu dosyadan yükler."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_dict = json.load(f)
                return AppConfig.from_dict(config_dict)
            else:
                # Varsayılan config oluştur ve kaydet
                default_config = self._get_default_config()
                self.save_config(default_config)
                return default_config
        except Exception as e:
            logging.warning(f"Config yükleme hatası: {e}. Varsayılan config kullanılıyor.")
            return self._get_default_config()
    
    def save_config(self, config: Optional[AppConfig] = None) -> bool:
        """Konfigürasyonu dosyaya kaydeder."""
        try:
            if config is None:
                config = self.config
            
            # Config dizinini oluştur
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
            
            self.config = config
            return True
        except Exception as e:
            logging.error(f"Config kaydetme hatası: {e}")
            return False
    
    def get_config(self) -> AppConfig:
        """Mevcut konfigürasyonu döndürür."""
        return self.config
    
    def update_config(self, **kwargs) -> bool:
        """Konfigürasyonu günceller."""
        try:
            config_dict = self.config.to_dict()
            
            for key, value in kwargs.items():
                if '.' in key:
                    # Nested key (örn: "camera.width")
                    parts = key.split('.')
                    current = config_dict
                    for part in parts[:-1]:
                        if part not in current:
                            current[part] = {}
                        current = current[part]
                    current[parts[-1]] = value
                else:
                    config_dict[key] = value
            
            new_config = AppConfig.from_dict(config_dict)
            return self.save_config(new_config)
        except Exception as e:
            logging.error(f"Config güncelleme hatası: {e}")
            return False
    
    def reset_to_default(self) -> bool:
        """Konfigürasyonu varsayılana sıfırlar."""
        default_config = self._get_default_config()
        return self.save_config(default_config)
    
    def get_camera_config(self) -> CameraConfig:
        """Kamera konfigürasyonu döndürür."""
        return self.config.camera
    
    def get_detection_config(self) -> DetectionConfig:
        """Algılama konfigürasyonu döndürür."""
        return self.config.detection
    
    def get_system_config(self) -> SystemConfig:
        """Sistem konfigürasyonu döndürür."""
        return self.config.system
    
    def get_ui_config(self) -> UIConfig:
        """UI konfigürasyonu döndürür."""
        return self.config.ui


# Global config instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Global config manager'ı döndürür."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> AppConfig:
    """Global konfigürasyonu döndürür."""
    return get_config_manager().get_config()


# Convenience functions
def get_camera_config() -> CameraConfig:
    """Kamera konfigürasyonu döndürür."""
    return get_config().camera


def get_detection_config() -> DetectionConfig:
    """Algılama konfigürasyonu döndürür."""
    return get_config().detection


def get_system_config() -> SystemConfig:
    """Sistem konfigürasyonu döndürür."""
    return get_config().system


def get_ui_config() -> UIConfig:
    """UI konfigürasyonu döndürür."""
    return get_config().ui 