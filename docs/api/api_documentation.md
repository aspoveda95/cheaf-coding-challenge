# Documentación de la API - Sistema Flash Promos

## Introducción

Esta documentación describe todos los endpoints disponibles en la API del sistema de Flash Promos. La API está construida con Django REST Framework y sigue los principios REST.

## Base URL

```
http://localhost:8000/api/
```

## Autenticación

Actualmente la API no requiere autenticación para simplificar las pruebas. En producción se recomienda implementar JWT tokens.

## Formato de Respuesta

Todas las respuestas siguen el formato JSON estándar:

```json
{
  "field": "value",
  "nested_object": {
    "nested_field": "nested_value"
  }
}
```

## Códigos de Estado HTTP

- `200 OK`: Operación exitosa
- `201 Created`: Recurso creado exitosamente
- `400 Bad Request`: Datos de entrada inválidos
- `404 Not Found`: Recurso no encontrado
- `409 Conflict`: Conflicto (ej: producto ya reservado)
- `500 Internal Server Error`: Error interno del servidor

## Endpoints de Flash Promos

### Crear Flash Promo

**POST** `/api/flash-promos/`

Crea una nueva promoción flash.

#### Request Body

```json
{
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
}
```

#### Response (201 Created)

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174002",
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
  "max_radius_km": 2.0,
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Obtener Promociones Activas

**GET** `/api/flash-promos/active/`

Obtiene todas las promociones flash actualmente activas.

#### Response (200 OK)

```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174002",
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
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

### Activar Flash Promo

**POST** `/api/flash-promos/activate/`

Activa una promoción flash específica.

#### Request Body

```json
{
  "promo_id": "123e4567-e89b-12d3-a456-426614174002"
}
```

#### Response (200 OK)

```json
{
  "message": "Flash promo activated successfully",
  "promo_id": "123e4567-e89b-12d3-a456-426614174002"
}
```

### Verificar Elegibilidad

**POST** `/api/flash-promos/eligibility/`

Verifica si un usuario es elegible para una promoción específica.

#### Request Body

```json
{
  "promo_id": "123e4567-e89b-12d3-a456-426614174002",
  "user_id": "123e4567-e89b-12d3-a456-426614174003"
}
```

#### Response (200 OK)

```json
{
  "eligible": true,
  "reason": "User is eligible"
}
```

### Estadísticas de Promoción

**GET** `/api/flash-promos/{promo_id}/statistics/`

Obtiene estadísticas detalladas de una promoción específica.

#### Response (200 OK)

```json
{
  "promo_id": "123e4567-e89b-12d3-a456-426614174002",
  "is_active": true,
  "eligible_users_count": 150,
  "user_segments": ["new_users", "frequent_buyers"],
  "time_range": "17:00:00 - 19:00:00",
  "promo_price": "$50.00"
}
```

## Endpoints de Reservas

### Reservar Producto

**POST** `/api/reservations/`

Reserva un producto durante una promoción flash.

#### Request Body

```json
{
  "product_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "123e4567-e89b-12d3-a456-426614174003",
  "flash_promo_id": "123e4567-e89b-12d3-a456-426614174002",
  "reservation_duration_minutes": 1
}
```

#### Response (201 Created)

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174004",
  "product_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "123e4567-e89b-12d3-a456-426614174003",
  "flash_promo_id": "123e4567-e89b-12d3-a456-426614174002",
  "created_at": "2024-01-15T10:30:00Z",
  "expires_at": "2024-01-15T10:31:00Z",
  "time_remaining_seconds": 60
}
```

#### Response (409 Conflict)

```json
{
  "error": "Product is already reserved or promo is not active"
}
```

### Estado de Reserva

**GET** `/api/reservations/{reservation_id}/status/`

Obtiene el estado actual de una reserva.

#### Response (200 OK)

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174004",
  "is_expired": false,
  "time_remaining_seconds": 45,
  "expires_at": "2024-01-15T10:31:00Z"
}
```

### Procesar Compra

**POST** `/api/reservations/purchase/`

Procesa la compra de un producto reservado.

#### Request Body

```json
{
  "reservation_id": "123e4567-e89b-12d3-a456-426614174004",
  "user_id": "123e4567-e89b-12d3-a456-426614174003"
}
```

#### Response (200 OK)

```json
{
  "success": true,
  "message": "Purchase completed successfully",
  "purchase_price": 50.0
}
```

### Verificar Disponibilidad

**GET** `/api/reservations/product/{product_id}/availability/`

Verifica si un producto está disponible para reserva.

#### Response (200 OK)

```json
{
  "product_id": "123e4567-e89b-12d3-a456-426614174000",
  "is_available": true,
  "is_reserved": false
}
```

## Endpoints de Usuarios

### Crear Usuario

**POST** `/api/users/`

Crea un nuevo usuario en el sistema.

#### Request Body

```json
{
  "email": "usuario@example.com",
  "name": "Usuario Test",
  "location": {
    "latitude": "40.7128",
    "longitude": "-74.0060"
  }
}
```

#### Response (201 Created)

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174003",
  "email": "usuario@example.com",
  "name": "Usuario Test",
  "location": {
    "latitude": "40.7128",
    "longitude": "-74.0060"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "last_purchase_at": null,
  "total_purchases": 0,
  "total_spent": "0.00",
  "segments": []
}
```

### Obtener Usuario

**GET** `/api/users/{user_id}/`

Obtiene información detallada de un usuario específico.

#### Response (200 OK)

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174003",
  "email": "usuario@example.com",
  "name": "Usuario Test",
  "location": {
    "latitude": "40.7128",
    "longitude": "-74.0060"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "last_purchase_at": "2024-01-15T09:15:00Z",
  "total_purchases": 5,
  "total_spent": "250.00",
  "segments": ["new_users", "frequent_buyers"]
}
```

### Actualizar Segmentos de Usuario

**POST** `/api/users/{user_id}/segments/`

Actualiza los segmentos de un usuario específico.

#### Request Body

```json
{
  "segments": ["new_users", "frequent_buyers", "vip_customers"]
}
```

#### Response (200 OK)

```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174003",
  "segments": ["new_users", "frequent_buyers", "vip_customers"],
  "is_new_user": true,
  "is_frequent_buyer": true,
  "is_vip_customer": false
}
```

### Estadísticas de Usuarios

**GET** `/api/users/statistics/`

Obtiene estadísticas generales de usuarios en el sistema.

#### Response (200 OK)

```json
{
  "total_users": 1000,
  "new_users": 150,
  "frequent_buyers": 300,
  "vip_customers": 50,
  "users_with_location": 800
}
```

## Endpoint de Health Check

### Health Check

**GET** `/health/`

Verifica el estado de salud del sistema y sus dependencias.

#### Response (200 OK)

```json
{
  "status": "healthy",
  "services": {
    "database": "healthy",
    "cache": "healthy",
    "redis": "healthy"
  }
}
```

#### Response (503 Service Unavailable)

```json
{
  "status": "unhealthy",
  "services": {
    "database": "healthy",
    "cache": "unhealthy",
    "redis": "unhealthy"
  }
}
```

## Segmentos de Usuario

Los siguientes segmentos están disponibles para las promociones:

- `new_users`: Usuarios nuevos (menos de 30 días)
- `frequent_buyers`: Compradores frecuentes (5+ compras en 90 días)
- `vip_customers`: Clientes VIP (gasto total > $1000)
- `location_based`: Basado en ubicación
- `time_based`: Basado en horarios
- `behavior_based`: Basado en comportamiento

## Códigos de Error Comunes

### 400 Bad Request

```json
{
  "error": "Invalid data provided",
  "details": {
    "field_name": ["Error message"]
  }
}
```

### 404 Not Found

```json
{
  "error": "Resource not found"
}
```

### 409 Conflict

```json
{
  "error": "Product is already reserved or promo is not active"
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal server error occurred"
}
```

## Ejemplos de Uso

### Flujo Completo de Flash Promo

1. **Crear promoción**:

```bash
curl -X POST http://localhost:8000/api/flash-promos/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "123e4567-e89b-12d3-a456-426614174000",
    "store_id": "123e4567-e89b-12d3-a456-426614174001",
    "promo_price": {"amount": "50.00", "currency": "USD"},
    "time_range": {"start_time": "17:00:00", "end_time": "19:00:00"},
    "user_segments": ["new_users", "frequent_buyers"],
    "max_radius_km": 2.0
  }'
```

2. **Verificar elegibilidad**:

```bash
curl -X POST http://localhost:8000/api/flash-promos/eligibility/ \
  -H "Content-Type: application/json" \
  -d '{
    "promo_id": "123e4567-e89b-12d3-a456-426614174002",
    "user_id": "123e4567-e89b-12d3-a456-426614174003"
  }'
```

3. **Reservar producto**:

```bash
curl -X POST http://localhost:8000/api/reservations/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "123e4567-e89b-12d3-a456-426614174000",
    "user_id": "123e4567-e89b-12d3-a456-426614174003",
    "flash_promo_id": "123e4567-e89b-12d3-a456-426614174002"
  }'
```

4. **Procesar compra**:

```bash
curl -X POST http://localhost:8000/api/reservations/purchase/ \
  -H "Content-Type: application/json" \
  -d '{
    "reservation_id": "123e4567-e89b-12d3-a456-426614174004",
    "user_id": "123e4567-e89b-12d3-a456-426614174003"
  }'
```

## Documentación Interactiva

Para una experiencia interactiva con la API, visita:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/schema/

Estas interfaces proporcionan documentación interactiva donde puedes probar los endpoints directamente desde el navegador.
