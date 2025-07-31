.PHONY: help build up down restart logs shell db-shell backup restore clean dev dev-down prod status health

# Configuración por defecto
COMPOSE_FILE := docker-compose.yml
DEV_COMPOSE_FILE := docker-compose.dev.yml
PROJECT_NAME := apg-bi-dashboard

# Colores para output
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m

help: ## 📖 Mostrar ayuda
	@echo "🐳 APG BI Dashboard - Comandos Docker"
	@echo "════════════════════════════════════════════════"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "$(BLUE)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "📝 EJEMPLOS:"
	@echo "  make dev          # Iniciar entorno de desarrollo"
	@echo "  make prod         # Desplegar en producción"
	@echo "  make backup       # Crear backup de la BD"
	@echo "  make logs         # Ver logs de todos los servicios"

# Comandos de Producción
build: ## 🔨 Construir imágenes Docker
	@echo -e "$(BLUE)Construyendo imágenes...$(NC)"
	docker-compose -f $(COMPOSE_FILE) build --no-cache

up: ## 🚀 Levantar servicios en producción
	@echo -e "$(BLUE)Levantando servicios de producción...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d

down: ## 🛑 Parar y eliminar servicios
	@echo -e "$(YELLOW)Parando servicios...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down

restart: ## 🔄 Reiniciar servicios
	@echo -e "$(BLUE)Reiniciando servicios...$(NC)"
	docker-compose -f $(COMPOSE_FILE) restart

# Comandos de Desarrollo
dev: ## 🔧 Iniciar entorno de desarrollo
	@echo -e "$(BLUE)Iniciando entorno de desarrollo...$(NC)"
	chmod +x docker/dev.sh
	./docker/dev.sh

dev-down: ## 🛑 Parar entorno de desarrollo
	@echo -e "$(YELLOW)Parando entorno de desarrollo...$(NC)"
	docker-compose -f $(DEV_COMPOSE_FILE) down

dev-logs: ## 📄 Ver logs de desarrollo
	docker-compose -f $(DEV_COMPOSE_FILE) logs -f

# Despliegue automatizado
prod: ## 🌟 Desplegar en producción (script completo)
	@echo -e "$(GREEN)Desplegando en producción...$(NC)"
	chmod +x docker/deploy.sh
	./docker/deploy.sh

# Logs y monitoring
logs: ## 📄 Ver logs de todos los servicios
	docker-compose -f $(COMPOSE_FILE) logs -f

logs-app: ## 📱 Ver logs solo de la aplicación
	docker-compose -f $(COMPOSE_FILE) logs -f dashboard-app

logs-db: ## 🗄️ Ver logs de la base de datos
	docker-compose -f $(COMPOSE_FILE) logs -f postgres-db

logs-nginx: ## 🌐 Ver logs de nginx
	docker-compose -f $(COMPOSE_FILE) logs -f nginx

# Shells y acceso
shell: ## 💻 Acceder al shell de la aplicación
	docker-compose -f $(COMPOSE_FILE) exec dashboard-app bash

db-shell: ## 🗄️ Acceder al shell de PostgreSQL
	chmod +x docker/db-utils.sh
	./docker/db-utils.sh shell

# Base de datos
backup: ## 💾 Crear backup de la base de datos
	@echo -e "$(BLUE)Creando backup...$(NC)"
	chmod +x docker/db-utils.sh
	./docker/db-utils.sh backup

restore: ## 🔄 Restaurar backup (make restore FILE=backup.sql.gz)
	@if [ -z "$(FILE)" ]; then \
		echo "❌ Especifica el archivo: make restore FILE=backup.sql.gz"; \
		exit 1; \
	fi
	chmod +x docker/db-utils.sh
	./docker/db-utils.sh restore $(FILE)

db-status: ## 📊 Ver estado de la base de datos
	chmod +x docker/db-utils.sh
	./docker/db-utils.sh status

db-reset: ## ⚠️ Resetear base de datos (¡PELIGROSO!)
	chmod +x docker/db-utils.sh
	./docker/db-utils.sh reset

# Monitoreo y salud
status: ## 📈 Ver estado de todos los servicios
	@echo -e "$(BLUE)Estado de los servicios:$(NC)"
	docker-compose -f $(COMPOSE_FILE) ps

health: ## 🏥 Verificar salud de la aplicación
	@echo -e "$(BLUE)Verificando salud de la aplicación...$(NC)"
	@curl -s http://localhost:8777/health | python -m json.tool || echo "❌ Aplicación no responde"

# Limpieza
clean: ## 🧹 Limpiar recursos Docker no utilizados
	@echo -e "$(YELLOW)Limpiando recursos Docker...$(NC)"
	docker system prune -f
	docker volume prune -f

clean-all: ## 🗑️ Limpieza completa (incluyendo imágenes)
	@echo -e "$(YELLOW)Limpieza completa...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down -v --rmi all
	docker-compose -f $(DEV_COMPOSE_FILE) down -v --rmi all
	docker system prune -af
	docker volume prune -f

# Información útil
info: ## ℹ️ Mostrar información del proyecto
	@echo -e "$(GREEN)📊 APG BI Dashboard - Información del Proyecto$(NC)"
	@echo "════════════════════════════════════════════════"
	@echo "🌐 URL Producción:  http://localhost:8777"
	@echo "🔧 URL Desarrollo:  http://localhost:8777"
	@echo "🗄️  PostgreSQL:     localhost:5432 (prod) / localhost:5433 (dev)"
	@echo "🔄 Redis:           localhost:6379"
	@echo "🌐 Nginx:           localhost:80"
	@echo ""
	@echo "📁 Archivos importantes:"
	@echo "  config.yaml             - Configuración principal (editable)"
	@echo "  config.docker.yaml      - Plantilla para producción"
	@echo "  config.dev.yaml         - Plantilla para desarrollo"
	@echo "  docker-compose.yml      - Configuración de producción"
	@echo "  docker-compose.dev.yml  - Configuración de desarrollo"
	@echo "  Dockerfile              - Imagen de producción"
	@echo "  Dockerfile.dev          - Imagen de desarrollo"
	@echo ""
	@echo "🔧 Scripts disponibles:"
	@echo "  docker/deploy.sh        - Script de despliegue automatizado"
	@echo "  docker/dev.sh          - Script de desarrollo"
	@echo "  docker/db-utils.sh     - Utilidades de base de datos"

# Instalación inicial
setup: ## ⚙️ Configuración inicial del proyecto
	@echo -e "$(BLUE)Configurando proyecto inicialmente...$(NC)"
	@if [ ! -f config.yaml ]; then \
		echo "Copiando configuración de Docker..."; \
		cp config.docker.yaml config.yaml; \
		echo -e "$(YELLOW)⚠️  Revisa config.yaml y actualiza las credenciales de Microsoft Graph$(NC)"; \
	fi
	@echo "Creando directorios necesarios..."
	mkdir -p logs backups docker/ssl
	@chmod +x docker/*.sh
	@echo -e "$(GREEN)✅ Configuración inicial completada$(NC)"
	@echo ""
	@echo "📝 Próximos pasos:"
	@echo "1. Edita config.yaml con tus credenciales de Microsoft Graph"
	@echo "2. Para desarrollo: make dev"
	@echo "3. Para producción: make prod"

# Configuración de entornos
config-dev: ## 🔧 Copiar configuración de desarrollo
	@echo -e "$(BLUE)Configurando para desarrollo...$(NC)"
	cp config.dev.yaml config.yaml
	@echo -e "$(GREEN)✅ Configuración de desarrollo aplicada$(NC)"

config-prod: ## 🚀 Copiar configuración de producción  
	@echo -e "$(BLUE)Configurando para producción...$(NC)"
	cp config.docker.yaml config.yaml
	@echo -e "$(GREEN)✅ Configuración de producción aplicada$(NC)"