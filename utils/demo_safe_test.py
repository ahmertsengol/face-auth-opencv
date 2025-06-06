#!/usr/bin/env python3
"""
Safe Demo Test - Professional Dashboard UI Test
OpenCV frame hatalarından korunmuş güvenli test
"""

import cv2
import numpy as np
import sys
from pathlib import Path

# Proje root dizinini ekle
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from main import OptimizedFaceRecognitionApp

def create_test_frame():
    """Test için örnek frame oluştur"""
    # 640x480 boyutunda test frame'i
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Gradient background
    for i in range(480):
        frame[i, :] = [i // 3, 50, 100]
    
    # Test face rectangle
    cv2.rectangle(frame, (200, 150), (400, 350), (0, 255, 0), 3)
    cv2.putText(frame, "TEST FACE", (250, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    return frame

def test_dashboard_ui():
    """Professional Dashboard UI Test"""
    print("🎯 Professional Dashboard UI Testi Başlatılıyor...")
    
    try:
        # App başlat
        app = OptimizedFaceRecognitionApp()
        
        # Test frame'i oluştur
        test_frame = create_test_frame()
        print(f"✅ Test frame oluşturuldu: {test_frame.shape}")
        
        # Test verileri
        fps_data = {
            'fps': 25.0,
            'frame_time': 16.5,
            'users': 2,
            'faces': 1,
            'cache_hits': 150,
            'memory': 45.2
        }
        
        registration_data = {
            'mode': 'REGISTRATION',
            'name': 'Demo User',
            'current': 3,
            'total': 5
        }
        
        recognition_data = {
            'last_recognition': {
                'name': 'Ahmet',
                'confidence': 0.95,
                'is_match': True
            }
        }
        
        # Dashboard UI testleri
        print("🎨 Dashboard UI çizimi test ediliyor...")
        
        # 1. Registration Mode
        result_frame = app._draw_dashboard_ui(test_frame.copy(), fps_data, registration_data=registration_data)
        print(f"✅ Registration UI: {result_frame.shape}")
        
        # 2. Recognition Mode  
        result_frame = app._draw_dashboard_ui(test_frame.copy(), fps_data, recognition_data=recognition_data)
        print(f"✅ Recognition UI: {result_frame.shape}")
        
        # 3. Face Overlay Test
        faces = [(200, 150, 200, 200)]  # Test face coordinates
        result_frame = app._draw_face_overlay(test_frame.copy(), faces, mode='registration')
        print(f"✅ Face Overlay: {result_frame.shape}")
        
        print("🎉 Dashboard UI Testleri Başarılı!")
        return True
        
    except Exception as e:
        print(f"❌ Test hatası: {e}")
        return False

if __name__ == "__main__":
    test_dashboard_ui() 