#!/bin/bash

# Script para ejecutar tests de forma eficiente usando base de datos local

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para mostrar mensajes
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Función de limpieza
cleanup() {
    log_info "🧹 Limpiando recursos..."
    # No hay nada que limpiar ya que usamos base de datos local
    log_success "Limpieza completada"
}

# Trap para limpieza en caso de error
trap cleanup EXIT

echo -e "${BLUE}🧪 Ejecutando tests con base de datos local...${NC}"

# Verificar que el archivo .env existe
if [ ! -f ".env" ]; then
    log_warning "Archivo .env no encontrado. Creando desde .env.example..."
    cp .env.example .env
    log_info "Por favor revisa y ajusta las credenciales en .env si es necesario."
fi

# Cargar variables de entorno
if [ -f ".env" ]; then
    log_info "📋 Cargando variables de entorno desde .env..."
    set -a  # automatically export all variables
    source .env
    set +a
fi

# Verificar conexión a base de datos de testing
log_info "🔍 Verificando conexión a base de datos de testing..."
if ! python manage.py check --deploy 2>/dev/null; then
    log_error "No se puede conectar a la base de datos de testing."
    log_info "Verifica que tu base de datos esté ejecutándose y que las credenciales en .env sean correctas."
    exit 1
fi

# Ejecutar migraciones en base de datos de testing
log_info "🔄 Ejecutando migraciones en base de datos de testing..."
python manage.py migrate

# Ejecutar tests
log_info "🧪 Ejecutando tests..."
if [ $# -eq 0 ]; then
    # Sin argumentos, ejecutar todos los tests
    pytest --cov=src --cov-report=term-missing --cov-report=html --tb=short -v
else
    # Con argumentos, pasarlos a pytest
    pytest --cov=src --cov-report=term-missing --cov-report=html --tb=short -v "$@"
fi

TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -eq 0 ]; then
    log_success "🎉 ¡Todos los tests pasaron exitosamente!"
else
    log_error "❌ Algunos tests fallaron"
fi

# Mostrar reporte de cobertura si existe
if [ -d "htmlcov" ]; then
    log_info "📊 Reporte de cobertura disponible en: htmlcov/index.html"
fi

exit $TEST_EXIT_CODE
