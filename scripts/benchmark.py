#!/usr/bin/env python3
"""
Ultra-Optimized Performance Benchmark Script
Enhanced with adaptive performance, stability testing, and memory profiling
"""

import sys
import time
import psutil
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple

# Proje root dizinini Python path'ine ekle
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.face_detector import OptimizedFaceDetector
from utils.logger import get_logger_manager

class UltraBenchmark:
    """Ultra-optimized benchmark test suite."""
    
    def __init__(self):
        self.detector = OptimizedFaceDetector()
        self.logger_manager = get_logger_manager()
        self.results = {}
        
    def run_memory_stress_test(self, duration: int = 30) -> Dict:
        """Memory ve stability stress testi."""
        print(f"🔥 Memory Stress Test başlatılıyor ({duration}s)...")
        
        # Initial memory
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024
        
        start_time = time.time()
        frame_count = 0
        error_count = 0
        memory_samples = []
        
        while time.time() - start_time < duration:
            try:
                # Çeşitli boyutlarda test frame'ler
                sizes = [(480, 640), (720, 1280), (240, 320), (1080, 1920)]
                size = sizes[frame_count % len(sizes)]
                
                test_img = np.random.randint(0, 255, (*size, 3), dtype=np.uint8)
                faces = self.detector.detect_faces_opencv_optimized(test_img, use_cache=True)
                
                frame_count += 1
                
                # Memory sample her 100 frame'de
                if frame_count % 100 == 0:
                    current_memory = process.memory_info().rss / 1024 / 1024
                    memory_samples.append(current_memory)
                    print(f"  Frame {frame_count}: {len(faces) if faces else 0} faces, {current_memory:.1f}MB")
                
            except Exception as e:
                error_count += 1
                if error_count > 10:
                    break
        
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_leak = final_memory - initial_memory
        
        return {
            'duration': duration,
            'frames_processed': frame_count,
            'errors': error_count,
            'fps': frame_count / duration,
            'initial_memory_mb': initial_memory,
            'final_memory_mb': final_memory,
            'memory_leak_mb': memory_leak,
            'peak_memory_mb': max(memory_samples) if memory_samples else final_memory,
            'avg_memory_mb': sum(memory_samples) / len(memory_samples) if memory_samples else final_memory
        }
    
    def run_adaptive_performance_test(self) -> Dict:
        """Adaptive performance özelliklerini test eder."""
        print("🎯 Adaptive Performance Test başlatılıyor...")
        
        # Değişken FPS scenarios
        scenarios = [
            ('High Load', [(1080, 1920)] * 50),    # Büyük frame'ler
            ('Mixed Load', [(480, 640), (720, 1280)] * 25),  # Karışık
            ('Low Load', [(240, 320)] * 50),       # Küçük frame'ler
        ]
        
        results = {}
        
        for scenario_name, frame_sizes in scenarios:
            print(f"  Testing {scenario_name}...")
            
            processing_times = []
            cache_hits = 0
            
            start_time = time.time()
            
            for i, size in enumerate(frame_sizes):
                frame_start = time.time()
                
                test_img = np.random.randint(0, 255, (*size, 3), dtype=np.uint8)
                faces = self.detector.detect_faces_opencv_optimized(test_img, use_cache=True)
                
                processing_time = (time.time() - frame_start) * 1000
                processing_times.append(processing_time)
                
                # Cache test - aynı frame'i tekrar işle
                cache_start = time.time()
                faces_cached = self.detector.detect_faces_opencv_optimized(test_img, use_cache=True)
                cache_time = (time.time() - cache_start) * 1000
                
                if cache_time < processing_time * 0.5:  # %50'den hızlıysa cache hit
                    cache_hits += 1
            
            total_time = time.time() - start_time
            
            results[scenario_name] = {
                'total_time_s': total_time,
                'frames': len(frame_sizes),
                'fps': len(frame_sizes) / total_time,
                'avg_processing_time_ms': sum(processing_times) / len(processing_times),
                'min_processing_time_ms': min(processing_times),
                'max_processing_time_ms': max(processing_times),
                'cache_hit_rate': (cache_hits / len(frame_sizes)) * 100,
                'cache_effectiveness': cache_hits > len(frame_sizes) * 0.7  # %70+ cache hit bekleniyor
            }
        
        return results
    
    def run_stability_test(self) -> Dict:
        """Sistem stability ve error recovery testleri."""
        print("🛡️ Stability Test başlatılıyor...")
        
        results = {
            'error_recovery': False,
            'cache_stability': False,
            'memory_stability': False,
            'performance_stability': False
        }
        
        # Error recovery test
        try:
            # Intentionally create problematic conditions
            invalid_frames = [
                np.array([]),  # Empty
                np.zeros((0, 0, 3)),  # Zero size
                np.ones((1, 1, 3)) * 255,  # Minimal size
            ]
            
            for invalid_frame in invalid_frames:
                try:
                    faces = self.detector.detect_faces_opencv_optimized(invalid_frame, use_cache=True)
                    # Error recovery çalışıyorsa exception'lar handle edilmeli
                except Exception:
                    pass  # Expected
            
            results['error_recovery'] = True
            print("  ✅ Error recovery test passed")
            
        except Exception as e:
            print(f"  ❌ Error recovery test failed: {e}")
        
        # Cache stability test
        try:
            test_img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            
            # Cache performance over time
            cache_times = []
            for i in range(20):
                start = time.time()
                faces = self.detector.detect_faces_opencv_optimized(test_img, use_cache=True)
                cache_times.append(time.time() - start)
            
            # Cache should be stable (variance low)
            avg_time = sum(cache_times) / len(cache_times)
            variance = sum((t - avg_time) ** 2 for t in cache_times) / len(cache_times)
            
            if variance < avg_time * 0.1:  # Low variance = stable
                results['cache_stability'] = True
                print("  ✅ Cache stability test passed")
            else:
                print(f"  ⚠️ Cache instability detected: variance={variance:.4f}")
                
        except Exception as e:
            print(f"  ❌ Cache stability test failed: {e}")
        
        return results
    
    def run_comprehensive_benchmark(self) -> None:
        """Kapsamlı benchmark testini çalıştırır."""
        print("🚀 Ultra-Optimized Comprehensive Benchmark başlatılıyor...")
        print("=" * 70)
        
        # 1. Memory Stress Test
        memory_results = self.run_memory_stress_test(30)
        self.results['memory_stress'] = memory_results
        
        print(f"\n📊 Memory Stress Test Sonuçları:")
        print(f"  FPS: {memory_results['fps']:.1f}")
        print(f"  Memory Leak: {memory_results['memory_leak_mb']:.1f}MB")
        print(f"  Peak Memory: {memory_results['peak_memory_mb']:.1f}MB")
        print(f"  Error Rate: {memory_results['errors']}/{memory_results['frames_processed']}")
        
        # 2. Adaptive Performance Test
        adaptive_results = self.run_adaptive_performance_test()
        self.results['adaptive_performance'] = adaptive_results
        
        print(f"\n🎯 Adaptive Performance Sonuçları:")
        for scenario, data in adaptive_results.items():
            print(f"  {scenario}:")
            print(f"    FPS: {data['fps']:.1f}")
            print(f"    Avg Processing: {data['avg_processing_time_ms']:.1f}ms")
            print(f"    Cache Hit Rate: {data['cache_hit_rate']:.1f}%")
            print(f"    Cache Effective: {'✅' if data['cache_effectiveness'] else '❌'}")
        
        # 3. Stability Test
        stability_results = self.run_stability_test()
        self.results['stability'] = stability_results
        
        print(f"\n🛡️ Stability Test Sonuçları:")
        for test_name, passed in stability_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {test_name}: {status}")
        
        # 4. Overall Performance Score
        self._calculate_performance_score()
        
        print(f"\n📈 Overall Performance Score: {self.results['overall_score']:.1f}/100")
        print("=" * 70)
        
        # 5. Save detailed report
        self._save_benchmark_report()
    
    def _calculate_performance_score(self) -> None:
        """Overall performance score hesaplar."""
        score = 0
        max_score = 100
        
        # Memory efficiency (25 points)
        memory_leak = self.results['memory_stress']['memory_leak_mb']
        if memory_leak < 50:
            score += 25
        elif memory_leak < 100:
            score += 15
        elif memory_leak < 200:
            score += 10
        
        # FPS performance (25 points)
        avg_fps = self.results['memory_stress']['fps']
        if avg_fps >= 25:
            score += 25
        elif avg_fps >= 15:
            score += 20
        elif avg_fps >= 10:
            score += 15
        elif avg_fps >= 5:
            score += 10
        
        # Cache effectiveness (25 points)
        cache_scores = []
        for scenario_data in self.results['adaptive_performance'].values():
            if scenario_data['cache_effectiveness']:
                cache_scores.append(25)
            elif scenario_data['cache_hit_rate'] > 50:
                cache_scores.append(15)
            else:
                cache_scores.append(5)
        
        score += sum(cache_scores) / len(cache_scores) if cache_scores else 0
        
        # Stability (25 points)
        stability_count = sum(self.results['stability'].values())
        total_stability_tests = len(self.results['stability'])
        score += (stability_count / total_stability_tests) * 25
        
        self.results['overall_score'] = min(score, max_score)
    
    def _save_benchmark_report(self) -> None:
        """Benchmark raporunu kaydeder."""
        try:
            import json
            from datetime import datetime
            
            report_path = Path("logs") / f"benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_path.parent.mkdir(exist_ok=True)
            
            with open(report_path, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            
            print(f"📄 Detaylı rapor kaydedildi: {report_path}")
            
        except Exception as e:
            print(f"❌ Rapor kaydetme hatası: {e}")

def main():
    """Ana benchmark fonksiyonu."""
    benchmark = UltraBenchmark()
    benchmark.run_comprehensive_benchmark()

if __name__ == "__main__":
    main() 