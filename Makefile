# Makefile para Flash Promos API

.PHONY: help test test-local test-isolated test-unit test-integration test-coverage clean build up down logs shell

# Variables
DOCKER_COMPOSE = docker compose

help: ## Mostrar ayuda
	@echo "Comandos disponibles:"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  test              - Ejecutar tests con base de datos local"
	@echo "  test-coverage     - Ejecutar tests con cobertura"
	@echo "  test-unit         - Ejecutar solo tests unitarios"
	@echo "  test-integration  - Ejecutar solo tests de integración"
	@echo "  setup-db          - Configurar bases de datos locales"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  build             - Construir imágenes"
	@echo "  up                - Iniciar servicios"
	@echo "  down              - Detener servicios"
	@echo "  logs              - Ver logs de servicios"
	@echo "  shell             - Abrir shell en contenedor web"
	@echo ""
	@echo "🧹 Limpieza:"
	@echo "  clean             - Limpiar contenedores y volúmenes"

# Testing targets
test: ## Ejecutar tests con base de datos local
	./scripts/run_tests.sh

test-coverage: ## Ejecutar tests con cobertura
	./scripts/run_tests.sh

test-unit: ## Ejecutar solo tests unitarios
	./scripts/run_tests.sh tests/unit/

test-integration: ## Ejecutar solo tests de integración
	./scripts/run_tests.sh tests/integration/

setup-db: ## Configurar variables de entorno (copiar .env.example a .env)
	cp .env.example .env
	@echo "Archivo .env creado. Por favor edita DATABASE_URL y REDIS_URL según tu configuración."

build: ## Construir imágenes
	$(DOCKER_COMPOSE) build

up: ## Iniciar servicios
	$(DOCKER_COMPOSE) up -d

down: ## Detener servicios
	$(DOCKER_COMPOSE) down

logs: ## Ver logs de servicios
	$(DOCKER_COMPOSE) logs -f

shell: ## Abrir shell en contenedor web
	$(DOCKER_COMPOSE) exec web bash

clean: ## Limpiar contenedores y volúmenes
	$(DOCKER_COMPOSE) down -v --remove-orphans
	$(DOCKER_COMPOSE_TEST) down -v --remove-orphans
	docker system prune -f
