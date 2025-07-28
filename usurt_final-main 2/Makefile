.PHONY: help install test format lint run docker-build docker-run clean

# Переменные
PYTHON = python3
PIP = pip3
BOT_DIR = usurt_bot

help: ## Показать справку
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Установить зависимости
	$(PIP) install -r $(BOT_DIR)/requirements.txt
	$(PIP) install pytest pytest-asyncio black isort

test: ## Запустить тесты
	$(PYTHON) -m pytest $(BOT_DIR)/tests/ -v

format: ## Форматировать код
	black $(BOT_DIR)/
	isort $(BOT_DIR)/

lint: ## Проверить код
	black --check $(BOT_DIR)/
	isort --check-only $(BOT_DIR)/

run: ## Запустить бота
	$(PYTHON) $(BOT_DIR)/bot.py

docker-build: ## Собрать Docker образ
	docker build -t university-dating-bot -f $(BOT_DIR)/docker/Dockerfile .

docker-run: ## Запустить бота в Docker
	cd $(BOT_DIR)/docker && docker-compose up -d

docker-stop: ## Остановить бота в Docker
	cd $(BOT_DIR)/docker && docker-compose down

docker-logs: ## Показать логи Docker
	cd $(BOT_DIR)/docker && docker-compose logs -f

clean: ## Очистить временные файлы
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -f $(BOT_DIR)/bot.log
	rm -f *.db

setup: ## Настройка проекта
	@echo "Создание виртуального окружения..."
	$(PYTHON) -m venv .venv
	@echo "Активируйте виртуальное окружение:"
	@echo "source .venv/bin/activate  # Linux/Mac"
	@echo ".venv\\Scripts\\activate  # Windows"
	@echo ""
	@echo "Затем выполните: make install"

dev: ## Запуск в режиме разработки
	$(PYTHON) -m pytest $(BOT_DIR)/tests/ -v
	black $(BOT_DIR)/
	isort $(BOT_DIR)/
	$(PYTHON) $(BOT_DIR)/bot.py

# Команды для работы с базой данных
db-reset: ## Сбросить базу данных
	rm -f university_dating.db
	@echo "База данных сброшена"

db-backup: ## Создать резервную копию БД
	cp university_dating.db university_dating_backup_$$(date +%Y%m%d_%H%M%S).db
	@echo "Резервная копия создана"

# Команды для мониторинга
logs: ## Показать логи бота
	tail -f $(BOT_DIR)/bot.log

status: ## Показать статус бота
	@echo "Статус процессов:"
	@ps aux | grep bot.py | grep -v grep || echo "Бот не запущен"
	@echo ""
	@echo "Размер базы данных:"
	@ls -lh university_dating.db 2>/dev/null || echo "База данных не найдена" 