# Arquitectura Hexagonal - Sistema Flash Promos

## Introducción

Este documento describe la implementación de la arquitectura hexagonal (Ports & Adapters) en el sistema de Flash Promos, explicando las decisiones de diseño y la separación de responsabilidades.

## Principios de la Arquitectura Hexagonal

### 1. Separación de Responsabilidades

La arquitectura hexagonal divide el sistema en cuatro capas principales:

- **Domain Layer**: Contiene la lógica de negocio pura
- **Application Layer**: Orquesta los casos de uso
- **Infrastructure Layer**: Implementa adaptadores externos
- **Presentation Layer**: Expone la API REST

### 2. Inversión de Dependencias

Las dependencias apuntan hacia adentro, hacia el dominio:

- El dominio no conoce la infraestructura
- La aplicación define interfaces (ports)
- La infraestructura implementa adaptadores

## Estructura del Proyecto

```
src/
├── domain/                    # Capa de Dominio
│   ├── entities/              # Entidades de negocio
│   │   ├── user.py
│   │   ├── store.py
│   │   ├── product.py
│   │   ├── flash_promo.py
│   │   └── reservation.py
│   ├── value_objects/         # Objetos de valor
│   │   ├── price.py
│   │   ├── location.py
│   │   ├── time_range.py
│   │   └── user_segment.py
│   └── repositories/          # Interfaces de repositorios
│       ├── flash_promo_repository.py
│       ├── user_repository.py
│       └── reservation_repository.py
├── application/              # Capa de Aplicación
│   ├── use_cases/            # Casos de uso
│   │   ├── create_flash_promo.py
│   │   ├── activate_flash_promo.py
│   │   ├── reserve_product.py
│   │   └── process_purchase.py
│   └── services/             # Servicios de dominio
│       ├── user_segmentation_service.py
│       ├── notification_service.py
│       └── promo_activation_service.py
├── infrastructure/           # Capa de Infraestructura
│   ├── adapters/            # Adaptadores externos
│   │   ├── cache_adapter.py
│   │   └── notification_adapter.py
│   └── repositories/        # Implementaciones de repositorios
│       ├── django_flash_promo_repository.py
│       ├── django_user_repository.py
│       └── django_reservation_repository.py
└── presentation/             # Capa de Presentación
    ├── api/                 # Endpoints REST
    ├── serializers/         # Serializadores
    └── views/               # Vistas de la API
```

## Capa de Dominio

### Entidades

Las entidades representan conceptos del negocio con identidad única:

#### User

```python
class User:
    def __init__(self, email: str, name: str, location: Location):
        self._id = uuid4()
        self._email = email
        self._name = name
        self._location = location
        # ... otros atributos

    def is_new_user(self, days_threshold: int = 30) -> bool:
        # Lógica de negocio para determinar si es usuario nuevo
```

#### FlashPromo

```python
class FlashPromo:
    def __init__(self, product_id: UUID, store_id: UUID,
                 promo_price: Price, time_range: TimeRange):
        self._id = uuid4()
        self._product_id = product_id
        self._store_id = store_id
        self._promo_price = promo_price
        self._time_range = time_range

    def is_currently_active(self, current_time: datetime = None) -> bool:
        # Lógica para determinar si la promo está activa
```

### Value Objects

Los value objects representan conceptos sin identidad:

#### Price

```python
class Price:
    def __init__(self, amount: Decimal):
        if amount < 0:
            raise ValueError("Price cannot be negative")
        self._amount = amount

    def calculate_discount_percentage(self, original_price: Price) -> Decimal:
        # Cálculo de descuento
```

#### Location

```python
class Location:
    def __init__(self, latitude: Decimal, longitude: Decimal):
        # Validación de coordenadas
        self._latitude = latitude
        self._longitude = longitude

    def distance_to(self, other: Location) -> Decimal:
        # Cálculo de distancia usando fórmula de Haversine
```

### Repositorios (Ports)

Los repositorios definen interfaces para acceso a datos:

```python
class FlashPromoRepository(ABC):
    @abstractmethod
    def save(self, flash_promo: FlashPromo) -> FlashPromo:
        pass

    @abstractmethod
    def get_by_id(self, promo_id: UUID) -> Optional[FlashPromo]:
        pass

    @abstractmethod
    def get_active_promos(self) -> List[FlashPromo]:
        pass
```

## Capa de Aplicación

### Casos de Uso

Los casos de uso orquestan la lógica de negocio:

```python
class CreateFlashPromoUseCase:
    def __init__(self, flash_promo_repository: FlashPromoRepository,
                 user_repository: UserRepository):
        self._flash_promo_repository = flash_promo_repository
        self._user_repository = user_repository

    def execute(self, product_id: UUID, store_id: UUID,
                promo_price: Price, time_range: TimeRange,
                user_segments: Set[UserSegment]) -> FlashPromo:
        # Validaciones de negocio
        if not user_segments:
            raise ValueError("At least one user segment must be specified")

        # Crear entidad
        flash_promo = FlashPromo(
            product_id=product_id,
            store_id=store_id,
            promo_price=promo_price,
            time_range=time_range,
            user_segments=user_segments
        )

        # Persistir
        return self._flash_promo_repository.save(flash_promo)
```

### Servicios de Dominio

Los servicios encapsulan lógica de negocio compleja:

```python
class UserSegmentationService:
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    def segment_users_by_behavior(self, users: List[User]) -> dict:
        # Algoritmos de segmentación
        segments = {
            UserSegment.NEW_USERS: [],
            UserSegment.FREQUENT_BUYERS: [],
            UserSegment.VIP_CUSTOMERS: []
        }

        for user in users:
            if user.is_new_user():
                segments[UserSegment.NEW_USERS].append(user)
            # ... más lógica de segmentación
```

## Capa de Infraestructura

### Adaptadores (Adapters)

Los adaptadores implementan las interfaces definidas en el dominio:

```python
class DjangoFlashPromoRepository(FlashPromoRepository):
    def __init__(self):
        self._model = FlashPromoModel

    def save(self, flash_promo: FlashPromo) -> FlashPromo:
        # Mapeo entre entidad y modelo Django
        model_instance = self._create_model_from_entity(flash_promo)
        model_instance.save()
        return self._entity_from_model(model_instance)

    def get_by_id(self, promo_id: UUID) -> Optional[FlashPromo]:
        try:
            model_instance = self._model.objects.get(id=promo_id)
            return self._entity_from_model(model_instance)
        except self._model.DoesNotExist:
            return None
```

### Cache Adapter

```python
class CacheAdapter:
    def __init__(self):
        self._redis_client = redis.from_url(settings.REDIS_URL)

    def get(self, key: str) -> Optional[Any]:
        # Implementación de cache con Redis
        pass

    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        # Implementación de cache con TTL
        pass
```

## Capa de Presentación

### Vistas de la API

```python
@api_view(['POST'])
@permission_classes([AllowAny])
def create_flash_promo(request):
    serializer = FlashPromoCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Inicializar dependencias
        flash_promo_repo = DjangoFlashPromoRepository()
        user_repo = DjangoUserRepository()

        # Crear caso de uso
        create_use_case = CreateFlashPromoUseCase(flash_promo_repo, user_repo)

        # Ejecutar caso de uso
        flash_promo = create_use_case.execute(
            product_id=UUID(serializer.validated_data['product_id']),
            # ... otros parámetros
        )

        # Serializar respuesta
        response_serializer = FlashPromoResponseSerializer(flash_promo)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
```

## Ventajas de la Arquitectura Hexagonal

### 1. Testabilidad

- **Testing Unitario**: Fácil mocking de dependencias
- **Testing de Integración**: Aislamiento de capas
- **Testing de Contrato**: Verificación de interfaces

### 2. Flexibilidad

- **Cambio de Framework**: De Django a Flask/FastAPI sin afectar lógica
- **Cambio de Base de Datos**: De PostgreSQL a MongoDB
- **Cambio de Cache**: De Redis a Memcached

### 3. Mantenibilidad

- **Separación Clara**: Responsabilidades bien definidas
- **Bajo Acoplamiento**: Dependencias inyectadas
- **Alta Cohesión**: Lógica relacionada agrupada

## Patrones de Diseño Implementados

### 1. Repository Pattern

- Abstracción de acceso a datos
- Facilita testing con mocks
- Permite cambiar implementación

### 2. Factory Pattern

- Creación de notificaciones
- Generación de estrategias de segmentación

### 3. Observer Pattern

- Sistema de eventos para activación de promos
- Notificaciones asíncronas

### 4. Strategy Pattern

- Algoritmos de segmentación de usuarios
- Múltiples canales de notificación

## Principios SOLID Aplicados

### Single Responsibility Principle (SRP)

- Cada clase tiene una responsabilidad única
- Entidades solo contienen lógica de negocio
- Servicios solo orquestan casos de uso

### Open/Closed Principle (OCP)

- Extensible para nuevos tipos de promos
- Nuevos canales de notificación
- Nuevos algoritmos de segmentación

### Liskov Substitution Principle (LSP)

- Interfaces bien definidas para reemplazos
- Implementaciones intercambiables

### Interface Segregation Principle (ISP)

- Interfaces específicas para cada funcionalidad
- No dependencias innecesarias

### Dependency Inversion Principle (DIP)

- Dependencias inyectadas, no hardcodeadas
- Abstracciones no dependen de detalles

## Conclusión

La arquitectura hexagonal proporciona una base sólida para el sistema de Flash Promos, garantizando:

- **Escalabilidad**: Fácil adición de nuevas funcionalidades
- **Mantenibilidad**: Código organizado y comprensible
- **Testabilidad**: Testing exhaustivo en todas las capas
- **Flexibilidad**: Adaptación a cambios de requerimientos

Esta arquitectura permite que el sistema evolucione de manera controlada, manteniendo la integridad de la lógica de negocio y facilitando la integración con nuevos sistemas externos.
