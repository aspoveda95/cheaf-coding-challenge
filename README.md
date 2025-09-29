# Sistema Flash Promos - Marketplace

## Descripción

Sistema de promociones flash para marketplace implementado con arquitectura hexagonal, Django REST Framework y optimizado para manejar alta concurrencia y notificaciones masivas.

## Características Principales

- 🏗️ **Arquitectura Hexagonal**: Separación clara entre dominio, aplicación, infraestructura y presentación
- 🔧 **Inyección de Dependencias**: [Lagom](https://lagom-di.readthedocs.io/) para gestión automática de dependencias
- ⚡ **Alta Performance**: Cache distribuido con Redis y procesamiento asíncrono con Celery
- 🔒 **Manejo de Concurrencia**: Reservas temporales con locks distribuidos
- 📱 **Notificaciones Masivas**: Hasta 10,000 notificaciones por minuto
- 🧪 **Testing Completo**: Cobertura del 100% con pytest
- 🐳 **Dockerizado**: Un solo comando para levantar todo el sistema
- 📚 **Documentación API**: Swagger/OpenAPI integrado

## Arquitectura del Sistema

### Capas de la Arquitectura Hexagonal

```
├── domain/           # Entidades y reglas de negocio
├── application/      # Casos de uso y servicios
├── infrastructure/  # Adaptadores (DB, Cache, Notifications)
└── presentation/    # API endpoints (Django REST Framework)
```

### Inyección de Dependencias con Lagom

El sistema utiliza [Lagom](https://lagom-di.readthedocs.io/) para la gestión automática de dependencias, proporcionando:

- **Inversión de Dependencias**: Las dependencias se inyectan automáticamente
- **Testing Simplificado**: Fácil mocking y testing de componentes
- **Flexibilidad**: Cambio de implementaciones sin modificar código
- **Decoradores Mágicos**: Inyección automática con `@magic_bind_to_container`

#### Ejemplo de Uso

```python
from lagom import magic_bind_to_container
from src.infrastructure.container import container

@magic_bind_to_container(container._container)
def create_flash_promo(request, create_use_case: CreateFlashPromoUseCase):
    # create_use_case se inyecta automáticamente
    flash_promo = create_use_case.execute(...)
    return Response(flash_promo)
```

### Componentes Principales

- **Flash Promos**: Promociones con precios especiales y horarios específicos
- **Segmentación de Usuarios**: Nuevos usuarios, compradores frecuentes, VIP
- **Reservas Temporales**: Productos reservados por 1 minuto
- **Notificaciones**: Email y push notifications masivas
- **Geolocalización**: Filtrado por radio de 2km desde la tienda

## Instalación y Configuración

### Prerrequisitos

- Docker y Docker Compose
- Python 3.11+ (para desarrollo local)
- PostgreSQL 15+
- Redis 7+
- pyenv (para gestión de versiones de Python)
- pip (para gestión de dependencias)

### Instalación con Docker (Recomendado)

1. **Clonar el repositorio**

```bash
git clone <repository-url>
cd cheaf-coding-challenge
```

2. **Levantar el sistema completo**

```bash
docker-compose up --build
```

3. **Ejecutar migraciones**

```bash
docker-compose exec web python manage.py migrate
```

4. **Crear superusuario (opcional)**

```bash
docker-compose exec web python manage.py createsuperuser
```

5. **Acceder a la aplicación**

- API: http://localhost:8000/api/
- Documentación: http://localhost:8000/api/docs/
- Admin: http://localhost:8000/admin/

### Instalación para Desarrollo

#### Prerrequisitos Adicionales

**Instalar pyenv (si no lo tienes)**

```bash
# macOS con Homebrew
brew install pyenv

# Linux/Ubuntu
curl https://pyenv.run | bash

# Agregar a tu shell profile (.bashrc, .zshrc, etc.)
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
```

#### Configuración del Entorno

**Opción 1: Script Automatizado (Recomendado)**

```bash
# Configuración automática con pip
./scripts/setup_environment.sh
```

**Opción 2: Configuración Manual con pip**

```bash
# 1. Instalar Python 3.11.7
pyenv install 3.11.7

# 2. Crear entorno virtual
pyenv virtualenv 3.11.7 flash-promos-env
pyenv activate flash-promos-env

# 3. Instalar dependencias
pip install -r requirements/dev.txt

# 4. Configurar variables de entorno
cp .env.example .env
```

#### Verificación del Entorno

```bash
# Verificar configuración
python --version                    # Debe mostrar Python 3.11.7
which python                       # Debe apuntar al entorno virtual
pyenv version                      # Debe mostrar flash-promos-env
```

3. **Configurar variables de entorno**

```bash
# Copiar archivo de ejemplo y configurar
cp .env.example .env

# Editar el archivo .env con tus valores
nano .env  # o tu editor preferido
```

**Variables importantes a configurar:**

- `SECRET_KEY`: Generar una clave secreta única
- `DATABASE_URL`: URL de conexión a PostgreSQL (opcional, por defecto usa localhost)
- `REDIS_URL`: URL de conexión a Redis (opcional, por defecto usa localhost)

4. **Ejecutar migraciones**

```bash
python manage.py migrate
```

5. **Ejecutar servidor de desarrollo**

```bash
python manage.py runserver
```

## Uso de la API

### Endpoints Principales

#### Flash Promos

- `POST /api/flash-promos/` - Crear promoción
- `GET /api/flash-promos/active/` - Obtener promociones activas
- `POST /api/flash-promos/activate/` - Activar promoción
- `POST /api/flash-promos/eligibility/` - Verificar elegibilidad
- `GET /api/flash-promos/{id}/statistics/` - Estadísticas de promoción

#### Reservas

- `POST /api/reservations/` - Reservar producto
- `GET /api/reservations/{id}/status/` - Estado de reserva
- `POST /api/reservations/purchase/` - Procesar compra
- `GET /api/reservations/product/{id}/availability/` - Disponibilidad

#### Usuarios

- `POST /api/users/` - Crear usuario
- `GET /api/users/{id}/` - Obtener usuario
- `POST /api/users/{id}/segments/` - Actualizar segmentos
- `GET /api/users/statistics/` - Estadísticas de usuarios

### Ejemplos de Uso

#### Crear una Flash Promo

```bash
curl -X POST http://localhost:8000/api/flash-promos/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "123e4567-e89b-12d3-a456-426614174000",
    "store_id": "123e4567-e89b-12d3-a456-426614174001",
    "promo_price": {
      "amount": "50.00",
      "currency": "USD"
    },
    "time_range": {
      "start_time": "17:00:00",
      "end_time": "19:00:00"
    },
    "user_segments": ["new_users", "frequent_buyers"],
    "max_radius_km": 2.0
  }'
```

#### Reservar un Producto

```bash
curl -X POST http://localhost:8000/api/reservations/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "123e4567-e89b-12d3-a456-426614174002",
    "flash_promo_id": "123e4567-e89b-12d3-a456-426614174003",
    "reservation_duration_minutes": 1
  }'
```

#### Crear un Usuario

```bash
curl -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@example.com",
    "name": "Usuario Test",
    "location": {
      "latitude": "40.7128",
      "longitude": "-74.0060"
    }
  }'
```

## Gestión de Entornos con pyenv

### Comandos Útiles de pyenv

```bash
# Ver versiones de Python instaladas
pyenv versions

# Ver entorno actual
pyenv version

# Activar entorno
pyenv activate flash-promos-env

# Desactivar entorno
pyenv deactivate

# Configurar entorno para el proyecto
pyenv local flash-promos-env

# Eliminar entorno (si es necesario)
pyenv uninstall flash-promos-env
```

### Scripts de Automatización

El proyecto incluye scripts para facilitar la configuración:

```bash
# Configuración completa del entorno con pip
./scripts/setup_environment.sh

# O configuración manual
pip install -r requirements/dev.txt
```

### Troubleshooting

**Problema: pyenv no se reconoce**

```bash
# Agregar pyenv al PATH
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc
```

**Problema: Entorno no se activa automáticamente**

```bash
# Verificar archivo .python-version
cat .python-version

# Recrear si es necesario
echo "flash-promos-env" > .python-version
```

**Problema: Dependencias no se instalan**

```bash
# Verificar que el entorno está activo
pyenv version

# Reinstalar dependencias
pip install --upgrade pip
./scripts/install_requirements.sh development
```

## Configuración de Variables de Entorno

### Archivo .env.example

El proyecto incluye un archivo `.env.example` que sirve como plantilla para configurar las variables de entorno:

```bash
# Copiar y configurar
cp .env.example .env
```

### Variables Principales

- **`SECRET_KEY`**: Clave secreta de Django (generar una única)
- **`DATABASE_URL`**: URL de conexión a PostgreSQL
- **`REDIS_URL`**: URL de conexión a Redis
- **`EMAIL_*`**: Configuración de email para notificaciones
- **`FIREBASE_*`**: Configuración de push notifications
- **`TWILIO_*`**: Configuración de SMS

### Generar SECRET_KEY

```bash
# Generar una clave secreta única
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Gestión de Dependencias con pip

El proyecto utiliza pip para la gestión de dependencias con una estructura organizada:

### **Estructura de Dependencias:**

- **`requirements/`**: Carpeta con dependencias organizadas por entorno
  - **`base.txt`**: Dependencias principales (Django, DRF, Redis, Celery)
  - **`lint.txt`**: Herramientas de código (Black, Flake8, isort, pre-commit)
  - **`dev.txt`**: Herramientas de desarrollo (Debug Toolbar, Silk) + base + lint
  - **`testing.txt`**: Herramientas de testing (pytest, coverage, factory-boy) + base + lint
  - **`production.txt`**: Dependencias de producción (Gunicorn, WhiteNoise, Sentry) + base
  - **`docker.txt`**: Dependencias para Docker + production

### **Comandos Útiles:**

```bash
# Instalar dependencias base
pip install -r requirements/base.txt

# Instalar herramientas de código
pip install -r requirements/lint.txt

# Instalar para desarrollo completo
pip install -r requirements/dev.txt

# Instalar para testing completo
pip install -r requirements/testing.txt

# Instalar para producción
pip install -r requirements/production.txt

# Instalar para Docker
pip install -r requirements/docker.txt

# Ejecutar comandos
python manage.py runserver
pytest
black src/
```

## 🧪 Testing

### Entornos de Testing Disponibles

#### 1. **Testing Local Aislado** (Recomendado)

```bash
# Ejecutar todos los tests en entorno aislado
make test-local

# Tests con cobertura
make test-coverage

# Tests específicos
make test-unit
make test-integration
```

#### 2. **Testing Completamente Aislado** (CI/CD)

```bash
# Entorno completamente independiente
make test-isolated

# Para CI/CD
./scripts/ci_test.sh
```

#### 3. **Testing Manual** (Debugging)

```bash
# Tests en entorno existente
make test

# Tests específicos con verbose
make test-local -v tests/unit/test_domain_entities.py
```

### Características del Testing

- ✅ **109 Tests**: 100% pasando
- ✅ **Cobertura**: 60% del código
- ✅ **Entornos Aislados**: Testing sin interferencias
- ✅ **Limpieza Automática**: Recursos se limpian automáticamente
- ✅ **Reportes**: HTML y XML para CI/CD
- ✅ **CI/CD Ready**: Pipeline completo con GitHub Actions

### Comandos Útiles

```bash
# Ver ayuda completa
make help

# Limpiar entorno
make clean

# Ver logs
make logs

# Abrir shell
make shell
```

📚 **Documentación detallada**: [docs/TESTING.md](docs/TESTING.md)

## 🚀 CI/CD Pipeline

El proyecto incluye un pipeline completo de CI/CD con GitHub Actions:

### 🔄 Pipeline Automático

- ✅ **Tests**: 109 tests con cobertura del 60%
- ✅ **Code Quality**: Black, isort, Flake8, MyPy
- ✅ **Security**: Escaneo de vulnerabilidades con Trivy
- ✅ **Build**: Construcción de imagen Docker
- ✅ **Deploy**: Release automático en `main`

### 📊 Reportes Generados

- **Cobertura**: HTML y XML
- **Tests**: JUnit XML
- **Seguridad**: SARIF
- **Deploy**: Resumen automático

### 🎯 Triggers

- **Push a `dev`**: Tests + Quality
- **Pull Request**: Pipeline completo
- **Push a `main`**: Pipeline completo + Deploy

📚 **Documentación de workflows**: [.github/README.md](.github/README.md)

### Ejecutar Tests Localmente (Desarrollo)

#### Configuración Inicial

```bash
# 1. Configurar variables de entorno
make setup-db

# 2. Editar DATABASE_URL y REDIS_URL en .env según tu configuración
nano .env
```

#### Comandos de Testing

```bash
# Ejecutar todos los tests
make test

# Ejecutar tests con cobertura
make test-coverage

# Ejecutar tests específicos
make test tests/unit/test_infrastructure_services.py

# Ejecutar solo tests unitarios
make test-unit

# Ejecutar solo tests de integración
make test-integration
```

#### Para Desarrollo Avanzado

```bash
# Ejecutar tests directamente
./scripts/run_tests.sh

# Con argumentos específicos
./scripts/run_tests.sh tests/unit/test_infrastructure_services.py -v
```

### Cobertura de Tests

El proyecto mantiene una cobertura del 100% en:

- Entidades del dominio
- Value objects
- Casos de uso
- Servicios de aplicación
- Repositorios
- Endpoints de la API

## Calidad de Código

### Herramientas de Calidad

- **Black**: Formateo automático de código
- **isort**: Ordenamiento de imports
- **Flake8**: Linting y análisis estático
- **MyPy**: Verificación de tipos
- **Pre-commit**: Hooks de calidad automáticos

### Configuración de Pre-commit

```bash
# Instalar pre-commit
pip install pre-commit

# Instalar hooks
pre-commit install

# Ejecutar en todos los archivos
pre-commit run --all-files
```

## Monitoreo y Observabilidad

### Health Checks

- **Endpoint**: `GET /health/`
- **Servicios monitoreados**: Database, Cache, Redis
- **Estado**: Healthy/Unhealthy

### Logging

- **Nivel**: INFO por defecto, DEBUG en desarrollo
- **Formato**: Structured logging
- **Destino**: Console (configurable)

### Métricas

- **Response Time**: < 200ms para consultas
- **Throughput**: 10,000 notificaciones/minuto
- **Cache Hit Rate**: > 90%
- **Availability**: 99.9% uptime

## Optimizaciones de Performance

### Cache Strategy

- **Redis**: Cache distribuido
- **TTL**: Múltiples niveles (1 min, 30 min, 1 hora)
- **Invalidación**: Inteligente por eventos

### Base de Datos

- **Índices**: Optimizados para consultas frecuentes
- **Connection Pooling**: PgBouncer para conexiones
- **Read Replicas**: Para consultas de solo lectura

### Notificaciones

- **Celery**: Procesamiento asíncrono
- **Batch Processing**: Lotes de 1000 usuarios
- **Rate Limiting**: 1 notificación por usuario por día

## Seguridad

### Autenticación y Autorización

- **JWT Tokens**: Autenticación stateless
- **RBAC**: Control de acceso basado en roles
- **Rate Limiting**: Protección contra abuso

### Protección de Datos

- **Encriptación**: Datos sensibles encriptados
- **GDPR Compliance**: Cumplimiento de privacidad
- **Audit Logs**: Registro de actividades

## Despliegue

### Docker Compose

```bash
# Desarrollo
docker-compose up

# Producción
docker-compose -f docker-compose.prod.yml up -d
```

### Variables de Entorno

```bash
# Base de datos
DATABASE_URL=postgresql://user:password@host:port/database

# Cache
REDIS_URL=redis://host:port/db

# Celery
CELERY_BROKER_URL=redis://host:port/db
CELERY_RESULT_BACKEND=redis://host:port/db

# Seguridad
SECRET_KEY=your-secret-key
DEBUG=False
```

## Contribución

### Flujo de Desarrollo

1. Fork del repositorio
2. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -m 'Agregar nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

### Estándares de Código

- **Python**: PEP 8 con Black
- **Imports**: isort con perfil black
- **Testing**: pytest con cobertura 100%

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

**Nota**: Este sistema está diseñado para manejar alta concurrencia y notificaciones masivas. Para producción, se recomienda configurar monitoreo adicional y ajustar los parámetros de cache según las necesidades específicas.
