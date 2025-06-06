"""
Veritabanı entegrasyonu - SQLite ile optimize edilmiş veri yönetimi
"""

import sqlite3
import json
import pickle
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
import logging
from dataclasses import asdict
import numpy as np
from datetime import timedelta

from core.user_manager import UserData
from utils.logger import get_logger


class DatabaseManager:
    """
    SQLite veritabanı yönetimi sınıfı.
    Performance: Connection pooling, prepared statements, indexing
    """
    
    def __init__(self, db_path: str = "data/face_recognition.db"):
        """DatabaseManager başlatır."""
        self.db_path = Path(db_path)
        self.logger = get_logger('database')
        
        # Veritabanı dizinini oluştur
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Veritabanını başlat
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Veritabanı tablolarını oluşturur."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA foreign_keys = ON")
                
                # Users tablosu
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        is_active BOOLEAN DEFAULT 1,
                        metadata TEXT DEFAULT '{}'
                    )
                """)
                
                # Face encodings tablosu
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS face_encodings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        encoding_data BLOB NOT NULL,
                        confidence_score REAL DEFAULT 0.0,
                        created_at TEXT NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """)
                
                # Recognition logs tablosu
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS recognition_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        recognized_name TEXT,
                        confidence REAL NOT NULL,
                        timestamp TEXT NOT NULL,
                        is_successful BOOLEAN NOT NULL,
                        session_id TEXT,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                """)
                
                # Performance metrics tablosu
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        function_name TEXT NOT NULL,
                        execution_time REAL NOT NULL,
                        timestamp TEXT NOT NULL,
                        session_id TEXT,
                        additional_data TEXT DEFAULT '{}'
                    )
                """)
                
                # İndeksler
                conn.execute("CREATE INDEX IF NOT EXISTS idx_users_name ON users(name)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_face_encodings_user ON face_encodings(user_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_recognition_logs_timestamp ON recognition_logs(timestamp)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_recognition_logs_user ON recognition_logs(user_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_performance_metrics_function ON performance_metrics(function_name)")
                
                conn.commit()
                self.logger.info("✅ Veritabanı başarıyla başlatıldı.")
                
        except Exception as e:
            self.logger.error(f"❌ Veritabanı başlatma hatası: {e}")
            raise
    
    def save_user(self, user_data: UserData) -> bool:
        """
        Kullanıcıyı veritabanına kaydeder.
        
        Args:
            user_data: Kaydedilecek kullanıcı verisi
            
        Returns:
            Başarılı ise True
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Kullanıcıyı ekle
                cursor = conn.execute("""
                    INSERT INTO users (name, created_at, updated_at, metadata)
                    VALUES (?, ?, ?, ?)
                """, (
                    user_data.name,
                    user_data.created_at,
                    user_data.updated_at,
                    json.dumps({})
                ))
                
                user_id = cursor.lastrowid
                
                # Face encoding'leri ekle
                for encoding in user_data.face_encodings:
                    # NumPy array'ini binary data'ya çevir
                    encoding_blob = pickle.dumps(encoding)
                    
                    conn.execute("""
                        INSERT INTO face_encodings (user_id, encoding_data, created_at)
                        VALUES (?, ?, ?)
                    """, (
                        user_id,
                        encoding_blob,
                        datetime.now().isoformat()
                    ))
                
                conn.commit()
                self.logger.info(f"✅ Kullanıcı '{user_data.name}' veritabanına kaydedildi.")
                return True
                
        except sqlite3.IntegrityError:
            self.logger.warning(f"⚠️  Kullanıcı '{user_data.name}' zaten mevcut!")
            return False
        except Exception as e:
            self.logger.error(f"❌ Kullanıcı kaydetme hatası: {e}")
            return False
    
    def load_user(self, name: str) -> Optional[UserData]:
        """
        Kullanıcıyı veritabanından yükler.
        
        Args:
            name: Kullanıcı adı
            
        Returns:
            UserData objesi veya None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Kullanıcı bilgilerini al
                user_row = conn.execute("""
                    SELECT id, name, created_at, updated_at, metadata
                    FROM users
                    WHERE name = ? AND is_active = 1
                """, (name,)).fetchone()
                
                if not user_row:
                    return None
                
                user_id, name, created_at, updated_at, metadata = user_row
                
                # Face encoding'leri al
                encoding_rows = conn.execute("""
                    SELECT encoding_data
                    FROM face_encodings
                    WHERE user_id = ?
                    ORDER BY created_at
                """, (user_id,)).fetchall()
                
                # Binary data'yı NumPy array'ine çevir
                face_encodings = []
                for (encoding_blob,) in encoding_rows:
                    encoding = pickle.loads(encoding_blob)
                    face_encodings.append(encoding)
                
                return UserData(
                    name=name,
                    face_encodings=face_encodings,
                    created_at=created_at,
                    updated_at=updated_at
                )
                
        except Exception as e:
            self.logger.error(f"❌ Kullanıcı yükleme hatası: {e}")
            return None
    
    def load_all_users(self) -> List[UserData]:
        """
        Tüm aktif kullanıcıları yükler.
        
        Returns:
            UserData objelerinin listesi
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Tüm aktif kullanıcıları al
                user_rows = conn.execute("""
                    SELECT id, name, created_at, updated_at
                    FROM users
                    WHERE is_active = 1
                    ORDER BY created_at
                """).fetchall()
                
                users = []
                for user_id, name, created_at, updated_at in user_rows:
                    # Her kullanıcının encoding'lerini al
                    encoding_rows = conn.execute("""
                        SELECT encoding_data
                        FROM face_encodings
                        WHERE user_id = ?
                        ORDER BY created_at
                    """, (user_id,)).fetchall()
                    
                    # Binary data'yı NumPy array'ine çevir
                    face_encodings = []
                    for (encoding_blob,) in encoding_rows:
                        encoding = pickle.loads(encoding_blob)
                        face_encodings.append(encoding)
                    
                    if face_encodings:  # Sadece encoding'i olan kullanıcıları al
                        users.append(UserData(
                            name=name,
                            face_encodings=face_encodings,
                            created_at=created_at,
                            updated_at=updated_at
                        ))
                
                self.logger.info(f"📚 {len(users)} kullanıcı veritabanından yüklendi.")
                return users
                
        except Exception as e:
            self.logger.error(f"❌ Kullanıcılar yükleme hatası: {e}")
            return []
    
    def delete_user(self, name: str) -> bool:
        """
        Kullanıcıyı veritabanından siler (soft delete).
        
        Args:
            name: Silinecek kullanıcı adı
            
        Returns:
            Başarılı ise True
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    UPDATE users 
                    SET is_active = 0, updated_at = ?
                    WHERE name = ? AND is_active = 1
                """, (datetime.now().isoformat(), name))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    self.logger.info(f"✅ Kullanıcı '{name}' silindi.")
                    return True
                else:
                    self.logger.warning(f"⚠️  Kullanıcı '{name}' bulunamadı.")
                    return False
                    
        except Exception as e:
            self.logger.error(f"❌ Kullanıcı silme hatası: {e}")
            return False
    
    def user_exists(self, name: str) -> bool:
        """
        Kullanıcının varlığını kontrol eder.
        
        Args:
            name: Kontrol edilecek kullanıcı adı
            
        Returns:
            Kullanıcı varsa True
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                result = conn.execute("""
                    SELECT 1 FROM users
                    WHERE name = ? AND is_active = 1
                    LIMIT 1
                """, (name,)).fetchone()
                
                return result is not None
                
        except Exception as e:
            self.logger.error(f"❌ Kullanıcı kontrol hatası: {e}")
            return False
    
    def log_recognition(self, user_id: Optional[int], recognized_name: str, 
                       confidence: float, is_successful: bool, session_id: str = None) -> None:
        """
        Yüz tanıma sonucunu loglar.
        
        Args:
            user_id: Kullanıcı ID'si (varsa)
            recognized_name: Tanınan isim
            confidence: Güven skoru
            is_successful: Başarılı tanıma mı
            session_id: Session ID
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO recognition_logs 
                    (user_id, recognized_name, confidence, timestamp, is_successful, session_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    recognized_name,
                    confidence,
                    datetime.now().isoformat(),
                    is_successful,
                    session_id
                ))
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"❌ Recognition log hatası: {e}")
    
    def log_performance(self, function_name: str, execution_time: float, 
                       session_id: str = None, additional_data: Dict = None) -> None:
        """
        Performance metriğini loglar.
        
        Args:
            function_name: Fonksiyon adı
            execution_time: Çalışma süresi
            session_id: Session ID
            additional_data: Ek veriler
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO performance_metrics 
                    (function_name, execution_time, timestamp, session_id, additional_data)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    function_name,
                    execution_time,
                    datetime.now().isoformat(),
                    session_id,
                    json.dumps(additional_data or {})
                ))
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"❌ Performance log hatası: {e}")
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """
        Kullanıcı istatistiklerini döndürür.
        
        Returns:
            İstatistik dictionary'si
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Toplam kullanıcı sayısı
                total_users = conn.execute("""
                    SELECT COUNT(*) FROM users WHERE is_active = 1
                """).fetchone()[0]
                
                # Toplam encoding sayısı
                total_encodings = conn.execute("""
                    SELECT COUNT(*) FROM face_encodings fe
                    JOIN users u ON fe.user_id = u.id
                    WHERE u.is_active = 1
                """).fetchone()[0]
                
                # En aktif kullanıcılar (recognition log'larına göre)
                most_active = conn.execute("""
                    SELECT u.name, COUNT(rl.id) as recognition_count
                    FROM users u
                    LEFT JOIN recognition_logs rl ON u.id = rl.user_id
                    WHERE u.is_active = 1
                    GROUP BY u.id, u.name
                    ORDER BY recognition_count DESC
                    LIMIT 5
                """).fetchall()
                
                return {
                    'total_users': total_users,
                    'total_encodings': total_encodings,
                    'avg_encodings_per_user': total_encodings / total_users if total_users > 0 else 0,
                    'most_active_users': [{'name': name, 'recognitions': count} for name, count in most_active]
                }
                
        except Exception as e:
            self.logger.error(f"❌ İstatistik alma hatası: {e}")
            return {}
    
    def cleanup_old_logs(self, days: int = 30) -> int:
        """
        Eski logları temizler.
        
        Args:
            days: Silinecek log yaşı (gün)
            
        Returns:
            Silinen kayıt sayısı
        """
        try:
            # Güvenli tarih hesaplama
            cutoff_date = datetime.now() - timedelta(days=days)
            cutoff_str = cutoff_date.isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                # Recognition logs temizle
                cursor1 = conn.execute("""
                    DELETE FROM recognition_logs 
                    WHERE timestamp < ?
                """, (cutoff_str,))
                
                # Performance metrics temizle
                cursor2 = conn.execute("""
                    DELETE FROM performance_metrics 
                    WHERE timestamp < ?
                """, (cutoff_str,))
                
                deleted_count = cursor1.rowcount + cursor2.rowcount
                conn.commit()
                
                self.logger.info(f"🧹 {deleted_count} eski log kaydı temizlendi.")
                return deleted_count
                
        except Exception as e:
            self.logger.error(f"❌ Log temizleme hatası: {e}")
            return 0
    
    def backup_database(self, backup_path: str = None) -> bool:
        """
        Veritabanı yedeği oluşturur.
        
        Args:
            backup_path: Yedek dosya yolu
            
        Returns:
            Başarılı ise True
        """
        try:
            if backup_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"data/backups/face_recognition_backup_{timestamp}.db"
            
            backup_path = Path(backup_path)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            with sqlite3.connect(self.db_path) as source:
                with sqlite3.connect(backup_path) as backup:
                    source.backup(backup)
            
            self.logger.info(f"💾 Veritabanı yedeği oluşturuldu: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Yedekleme hatası: {e}")
            return False


# Global instance
_database_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """Global database manager döndürür."""
    global _database_manager
    if _database_manager is None:
        _database_manager = DatabaseManager()
    return _database_manager