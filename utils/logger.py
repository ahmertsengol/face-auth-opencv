"""
Gelişmiş logging sistemi
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import json
import traceback
from functools import wraps


class ColoredFormatter(logging.Formatter):
    """Renkli console output için formatter."""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


class PerformanceLogger:
    """Performance metriklerini loglar."""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {}
        self.logger = logging.getLogger('performance')
    
    def log_execution_time(self, function_name: str, execution_time: float):
        """Fonksiyon çalışma süresini loglar."""
        if function_name not in self.metrics:
            self.metrics[function_name] = {
                'total_calls': 0,
                'total_time': 0.0,
                'avg_time': 0.0,
                'max_time': 0.0,
                'min_time': float('inf')
            }
        
        metrics = self.metrics[function_name]
        metrics['total_calls'] += 1
        metrics['total_time'] += execution_time
        metrics['avg_time'] = metrics['total_time'] / metrics['total_calls']
        metrics['max_time'] = max(metrics['max_time'], execution_time)
        metrics['min_time'] = min(metrics['min_time'], execution_time)
        
        self.logger.debug(f"{function_name}: {execution_time:.4f}s")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Performance metriklerini döndürür."""
        return self.metrics.copy()
    
    def reset_metrics(self):
        """Metrikleri sıfırlar."""
        self.metrics.clear()


class LoggerManager:
    """Merkezi logger yönetimi."""
    
    def __init__(self, 
                 log_dir: str = "logs",
                 log_level: str = "INFO",
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5):
        """LoggerManager başlatır."""
        self.log_dir = Path(log_dir)
        self.log_level = getattr(logging, log_level.upper())
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        
        # Log dizinini oluştur
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Performance logger
        self.performance = PerformanceLogger()
        
        # Ana logger'ı kur
        self._setup_main_logger()
        
        # Component loggerları
        self.loggers = {}
    
    def _setup_main_logger(self):
        """Ana logger kurulumu."""
        # Root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        
        # Temizle
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # File handler
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            self.log_dir / "app.log",
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """Component logger döndürür."""
        if name not in self.loggers:
            logger = logging.getLogger(name)
            self.loggers[name] = logger
        return self.loggers[name]
    
    def log_error_with_traceback(self, logger: logging.Logger, message: str, exc: Exception):
        """Hata ve traceback'i loglar."""
        logger.error(f"{message}: {str(exc)}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
    
    def log_system_info(self):
        """Sistem bilgilerini loglar."""
        import platform
        import psutil
        
        logger = self.get_logger('system')
        logger.info(f"Platform: {platform.platform()}")
        logger.info(f"Python: {platform.python_version()}")
        logger.info(f"CPU: {psutil.cpu_count()} cores")
        logger.info(f"Memory: {psutil.virtual_memory().total // (1024**3)} GB")
    
    def create_performance_report(self) -> str:
        """Performance raporu oluşturur."""
        metrics = self.performance.get_metrics()
        
        report = ["Performance Report", "=" * 50]
        for func_name, data in metrics.items():
            report.append(f"Function: {func_name}")
            report.append(f"  Total calls: {data['total_calls']}")
            report.append(f"  Avg time: {data['avg_time']:.4f}s")
            report.append(f"  Max time: {data['max_time']:.4f}s")
            report.append(f"  Min time: {data['min_time']:.4f}s")
            report.append("")
        
        return "\n".join(report)
    
    def save_performance_report(self) -> bool:
        """Performance raporunu dosyaya kaydeder."""
        try:
            report_path = self.log_dir / f"performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(self.create_performance_report())
            return True
        except Exception as e:
            logging.error(f"Performance raporu kaydedilemedi: {e}")
            return False


# Decorators
def log_execution_time(logger_name: str = None):
    """Fonksiyon çalışma süresini loglar."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Global logger manager'dan performance logger'ı kullan
                if hasattr(wrapper, '_logger_manager'):
                    wrapper._logger_manager.performance.log_execution_time(
                        func.__name__, execution_time
                    )
                
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger = logging.getLogger(logger_name or func.__module__)
                logger.error(f"{func.__name__} failed after {execution_time:.4f}s: {e}")
                raise
        
        return wrapper
    return decorator


def log_method_calls(logger_name: str = None):
    """Method çağrılarını loglar."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(logger_name or func.__module__)
            logger.debug(f"Calling {func.__name__} with args={args[1:]} kwargs={kwargs}")
            
            try:
                result = func(*args, **kwargs)
                logger.debug(f"{func.__name__} completed successfully")
                return result
            except Exception as e:
                logger.error(f"{func.__name__} failed: {e}")
                raise
        
        return wrapper
    return decorator


# Global logger manager instance
_logger_manager: Optional[LoggerManager] = None


def get_logger_manager() -> LoggerManager:
    """Global logger manager döndürür."""
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = LoggerManager()
    return _logger_manager


def get_logger(name: str) -> logging.Logger:
    """Component logger döndürür."""
    return get_logger_manager().get_logger(name)


def setup_logging(log_dir: str = "logs", log_level: str = "INFO"):
    """Logging sistemini kurar."""
    global _logger_manager
    _logger_manager = LoggerManager(log_dir=log_dir, log_level=log_level)
    
    # Decorator'larda kullanım için
    for decorator_func in [log_execution_time]:
        if hasattr(decorator_func, '__call__'):
            decorator_func._logger_manager = _logger_manager
    
    return _logger_manager 