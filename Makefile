# Face Recognition System - Optimize Edilmiş Makefile
# Kullanım: make [komut]

# Değişkenler
VENV_NAME = venv_face_recognition
PYTHON = $(VENV_NAME)/bin/python
PIP = $(VENV_NAME)/bin/pip
PYTEST = $(VENV_NAME)/bin/pytest
REQUIREMENTS = config/requirements.txt
APP_CONFIG = config/app_config.json

# Renkler
RED = \033[0;31m
GREEN = \033[0;32m
YELLOW = \033[0;33m
BLUE = \033[0;34m
NC = \033[0m # No Color

.PHONY: help install test clean dev setup config optimize status benchmark backup logs monitor menu-delete

# Varsayılan hedef
all: help

help: ## Yardım menüsünü gösterir
	@echo "$(BLUE)🤖 Face Recognition System - Komutlar$(NC)"
	@echo "$(YELLOW)============================================$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-15s$(NC) %s\n", $$1, $$2}'

# Kurulum ve Kurulum İşlemleri
install: ## Sistemi kur (sanal ortam + paketler)
	@echo "$(BLUE)🚀 Face Recognition System kuruluyor...$(NC)"
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "$(YELLOW)📦 Sanal ortam oluşturuluyor...$(NC)"; \
		python3 -m venv $(VENV_NAME); \
	fi
	@echo "$(YELLOW)📚 Paketler yükleniyor...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r $(REQUIREMENTS)
	@echo "$(YELLOW)⚙️  Konfigürasyon oluşturuluyor...$(NC)"
	@$(MAKE) config
	@echo "$(GREEN)✅ Kurulum tamamlandı!$(NC)"
	@echo "$(BLUE)📖 Kullanım: make register / make recognize / make list$(NC)"

setup: install ## Alias for install

config: ## Konfigürasyon dosyası oluşturur
	@echo "$(YELLOW)⚙️  Konfigürasyon oluşturuluyor...$(NC)"
	@mkdir -p config data logs data/backups
	@if [ ! -f "$(APP_CONFIG)" ]; then \
		$(PYTHON) -c "from config.app_config import get_config_manager; get_config_manager().save_config()"; \
		echo "$(GREEN)✅ Konfigürasyon dosyası oluşturuldu: $(APP_CONFIG)$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  Konfigürasyon dosyası zaten mevcut$(NC)"; \
	fi

# Ana Komutlar
register: ## Yeni kullanıcı kaydet
	@echo "$(BLUE)📝 Kullanıcı kaydı başlatılıyor...$(NC)"
	@if [ ! -d "$(VENV_NAME)" ]; then echo "$(RED)❌ Önce 'make install' çalıştırın$(NC)"; exit 1; fi
	@read -p "Kullanıcı adı: " name; \
	if [ -z "$$name" ]; then \
		echo "$(RED)❌ Kullanıcı adı boş olamaz!$(NC)"; \
		exit 1; \
	fi; \
	$(PYTHON) main.py register --name "$$name"

recognize: ## Yüz tanıma başlat
	@echo "$(BLUE)🎯 Yüz tanıma başlatılıyor...$(NC)"
	@if [ ! -d "$(VENV_NAME)" ]; then echo "$(RED)❌ Önce 'make install' çalıştırın$(NC)"; exit 1; fi
	$(PYTHON) main.py recognize

list: ## Kullanıcıları listele
	@echo "$(BLUE)📋 Kullanıcılar listeleniyor...$(NC)"
	@if [ ! -d "$(VENV_NAME)" ]; then echo "$(RED)❌ Önce 'make install' çalıştırın$(NC)"; exit 1; fi
	$(PYTHON) main.py list-users

delete: ## Kullanıcı sil (make delete USER=isim)
	@echo "$(BLUE)🗑️  Kullanıcı siliniyor...$(NC)"
	@if [ ! -d "$(VENV_NAME)" ]; then echo "$(RED)❌ Önce 'make install' çalıştırın$(NC)"; exit 1; fi
	@if [ -z "$(USER)" ]; then echo "$(RED)❌ Kullanım: make delete USER=kullanici_adi$(NC)"; exit 1; fi
	$(PYTHON) main.py delete --name "$(USER)"

# Test ve Geliştirme
test: ## Sistem testleri çalıştır
	@echo "$(BLUE)🧪 Testler çalıştırılıyor...$(NC)"
	@if [ ! -d "$(VENV_NAME)" ]; then echo "$(RED)❌ Önce 'make install' çalıştırın$(NC)"; exit 1; fi
	$(PYTHON) scripts/test_system.py

dev: ## Geliştirme modunda çalıştır (debug logs)
	@echo "$(BLUE)🔧 Geliştirme modu başlatılıyor...$(NC)"
	@if [ ! -d "$(VENV_NAME)" ]; then echo "$(RED)❌ Önce 'make install' çalıştırın$(NC)"; exit 1; fi
	@$(PYTHON) -c "from config.app_config import get_config_manager; cm = get_config_manager(); cm.update_config(**{'system.log_level': 'DEBUG'})"
	@echo "$(GREEN)✅ Debug log seviyesi aktif$(NC)"

benchmark: ## Ultra-optimized performance benchmark çalıştır
	@echo "$(BLUE)⚡ Ultra-Optimized Performance benchmark başlatılıyor...$(NC)"
	@if [ ! -d "$(VENV_NAME)" ]; then echo "$(RED)❌ Önce 'make install' çalıştırın$(NC)"; exit 1; fi
	@$(PYTHON) scripts/benchmark.py

# Optimizasyon ve Bakım
optimize: ## Sistem optimizasyonu yap
	@echo "$(BLUE)⚡ Sistem optimizasyonu başlatılıyor...$(NC)"
	@if [ ! -d "$(VENV_NAME)" ]; then echo "$(RED)❌ Önce 'make install' çalıştırın$(NC)"; exit 1; fi
	@echo "$(YELLOW)🧹 Cache temizliği...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(YELLOW)📊 Veritabanı optimizasyonu...$(NC)"
	@$(PYTHON) -c "from utils.database import get_database_manager; db = get_database_manager(); cleaned = db.cleanup_old_logs(30); print(f'🧹 {cleaned} eski log kaydı temizlendi.'); stats = db.get_user_statistics(); print(f'📈 İstatistikler:'); print(f'  Kullanıcı sayısı: {stats.get(\"total_users\", 0)}'); print(f'  Encoding sayısı: {stats.get(\"total_encodings\", 0)}'); print(f'  Ortalama encoding/kullanıcı: {stats.get(\"avg_encodings_per_user\", 0):.1f}')"
	@echo "$(GREEN)✅ Optimizasyon tamamlandı!$(NC)"

backup: ## Veritabanı yedeği oluştur
	@echo "$(BLUE)💾 Veritabanı yedeği oluşturuluyor...$(NC)"
	@if [ ! -d "$(VENV_NAME)" ]; then echo "$(RED)❌ Önce 'make install' çalıştırın$(NC)"; exit 1; fi
	@$(PYTHON) -c "from utils.database import get_database_manager; db = get_database_manager(); print('✅ Yedekleme başarılı!' if db.backup_database() else '❌ Yedekleme hatası!')"

status: ## Sistem durumu göster
	@echo "$(BLUE)📊 Sistem Durumu$(NC)"
	@echo "$(YELLOW)==================$(NC)"
	@if [ -d "$(VENV_NAME)" ]; then \
		echo "$(GREEN)✅ Sanal ortam: Hazır$(NC)"; \
		$(PYTHON) --version | sed 's/^/  /'; \
	else \
		echo "$(RED)❌ Sanal ortam: Yok (make install çalıştırın)$(NC)"; \
	fi
	@if [ -f "$(APP_CONFIG)" ]; then \
		echo "$(GREEN)✅ Konfigürasyon: Hazır$(NC)"; \
		echo "  Dosya: $(APP_CONFIG)"; \
	else \
		echo "$(RED)❌ Konfigürasyon: Yok$(NC)"; \
	fi
	@if [ -d "data" ]; then \
		echo "$(GREEN)✅ Veri dizini: Hazır$(NC)"; \
		USER_COUNT=$$(find data -name "*.json" 2>/dev/null | wc -l); \
		echo "  Kullanıcı sayısı: $$USER_COUNT"; \
	else \
		echo "$(YELLOW)⚠️  Veri dizini: Yok$(NC)"; \
	fi
	@if [ -d "logs" ]; then \
		echo "$(GREEN)✅ Log dizini: Hazır$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  Log dizini: Yok$(NC)"; \
	fi

# Temizlik İşlemleri
clean: ## Cache ve geçici dosyaları temizle
	@echo "$(BLUE)🧹 Temizlik başlatılıyor...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@rm -rf .pytest_cache 2>/dev/null || true
	@echo "$(GREEN)✅ Temizlik tamamlandı$(NC)"

clean-venv: ## Sanal ortamı sil
	@echo "$(BLUE)🗑️  Sanal ortam siliniyor...$(NC)"
	@rm -rf $(VENV_NAME)
	@echo "$(GREEN)✅ Sanal ortam silindi$(NC)"

clean-all: clean clean-venv ## Her şeyi temizle
	@echo "$(BLUE)🗑️  Tam temizlik...$(NC)"
	@rm -rf data/backups/*.db 2>/dev/null || true
	@rm -rf logs/*.log 2>/dev/null || true
	@echo "$(GREEN)✅ Tam temizlik tamamlandı$(NC)"

# Ek Araçlar
update: ## Paketleri güncelle
	@echo "$(BLUE)📦 Paketler güncelleniyor...$(NC)"
	@if [ ! -d "$(VENV_NAME)" ]; then echo "$(RED)❌ Önce 'make install' çalıştırın$(NC)"; exit 1; fi
	$(PIP) install --upgrade pip
	$(PIP) install -r $(REQUIREMENTS) --upgrade
	@echo "$(GREEN)✅ Güncelleme tamamlandı$(NC)"

logs: ## Son logları göster
	@echo "$(BLUE)📄 Son loglar:$(NC)"
	@if [ -f "logs/app.log" ]; then tail -20 logs/app.log; else echo "$(YELLOW)⚠️  Log dosyası bulunamadı$(NC)"; fi

monitor: ## Sistem monitörü (gerçek zamanlı loglar)
	@echo "$(BLUE)👁️  Sistem monitörü başlatılıyor... (Ctrl+C ile çıkış)$(NC)"
	@if [ -f "logs/app.log" ]; then tail -f logs/app.log; else echo "$(YELLOW)⚠️  Log dosyası bulunamadı$(NC)"; fi

menu-delete: ## Anlık tuş yanıtlı interaktif kullanıcı silme menüsü
	@echo "$(BLUE)🎮 İnteraktif kullanıcı silme menüsü başlatılıyor...$(NC)"
	@if [ ! -d "$(VENV_NAME)" ]; then echo "$(RED)❌ Önce 'make install' çalıştırın$(NC)"; exit 1; fi
	$(PYTHON) main.py delete-interactive 