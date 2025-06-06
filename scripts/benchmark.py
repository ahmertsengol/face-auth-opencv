#!/usr/bin/env python3
"""
Performance Benchmark Script
"""

import sys
import time
from pathlib import Path
import numpy as np

# Proje root dizinini Python path'ine ekle
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.face_detector import OptimizedFaceDetector
from utils.logger import get_logger_manager

def main():
    """Ana benchmark fonksiyonu."""
    print("🔄 Benchmark çalıştırılıyor...")
    
    # Test image oluştur
    test_img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    detector = OptimizedFaceDetector()
    logger_manager = get_logger_manager()
    
    start_time = time.time()
    
    for i in range(100):
        faces = detector.detect_faces_opencv_optimized(test_img)
        if i % 20 == 0:
            print(f"  Frame {i+1}/100 - {len(faces) if faces else 0} faces")
    
    total_time = time.time() - start_time
    print(f"✅ Benchmark tamamlandı: {total_time:.2f}s, Ortalama: {total_time/100*1000:.1f}ms/frame")
    
    # Performance raporu
    print("\n📊 Performance Raporu:")
    print(logger_manager.create_performance_report())

if __name__ == "__main__":
    main() 