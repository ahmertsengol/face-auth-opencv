# Yüz Tanıma Sistemi - Makefile
# Kullanım: make <command>

PYTHON = python3
VENV_NAME = venv_face_recognition
VENV_ACTIVATE = source $(VENV_NAME)/bin/activate

# Sanal ortam kurulumu
install:
	@echo "🚀 Sanal ortam ve sistem kurulumu başlatılıyor..."
	$(PYTHON) -m venv $(VENV_NAME)
	$(VENV_ACTIVATE) && python scripts/setup_venv.py

# Sanal ortamı aktifleştir (bilgilendirme)
activate:
	@echo "🐍 Sanal ortamı aktifleştirmek için:"
	@echo "   source $(VENV_NAME)/bin/activate"
	@echo "   # veya"
	@echo "   ./scripts/activate_project.sh"

# Sistem testleri
test:
	@echo "🧪 Sistem testleri çalıştırılıyor..."
	$(VENV_ACTIVATE) && python scripts/test_system.py

# Kullanıcı kaydet
register:
	@echo "👤 Kullanıcı kaydı için isim girin:"
	@read -p "İsim: " name; \
	$(VENV_ACTIVATE) && python main.py register -n "$$name"

# Yüz tanıma başlat
recognize:
	@echo "👁️ Yüz tanıma başlatılıyor..."
	$(VENV_ACTIVATE) && python main.py recognize

# Kullanıcıları listele
list:
	@echo "📋 Kayıtlı kullanıcılar:"
	$(VENV_ACTIVATE) && python main.py list-users

# Temizlik
clean:
	@echo "🧹 Temizlik yapılıyor..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf logs/*.log
	rm -rf data/backups/*

# Sanal ortamı tamamen sil
clean-venv:
	@echo "🗑️ Sanal ortam siliniyor..."
	rm -rf $(VENV_NAME)
	@echo "✅ Sanal ortam silindi. Yeniden kurmak için 'make install' çalıştırın."

# Geliştirme araçları
dev-install:
	$(VENV_ACTIVATE) && pip install black flake8 pytest

# Kod formatlama
format:
	$(VENV_ACTIVATE) && black . --exclude $(VENV_NAME)

# Kod kalitesi kontrolü
lint:
	$(VENV_ACTIVATE) && flake8 . --exclude $(VENV_NAME)

# Yardım
help:
	@echo "🎯 Kullanılabilir Komutlar:"
	@echo "  install     - Projeyi kur (sanal ortam + paketler)"
	@echo "  activate    - Sanal ortam aktivasyon talimatları"
	@echo "  test        - Sistem testlerini çalıştır"
	@echo "  register    - Yeni kullanıcı kaydet"
	@echo "  recognize   - Yüz tanıma başlat"
	@echo "  list        - Kullanıcıları listele"
	@echo "  clean       - Geçici dosyaları temizle"
	@echo "  clean-venv  - Sanal ortamı tamamen sil"
	@echo "  dev-install - Geliştirme araçlarını kur"
	@echo "  format      - Kodu formatla (black)"
	@echo "  lint        - Kod kalitesi kontrolü (flake8)"
	@echo "  help        - Bu yardımı göster"

.PHONY: install activate test register recognize list clean clean-venv dev-install format lint help 