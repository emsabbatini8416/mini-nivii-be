# Mini Nivii Backend

API backend que permite realizar consultas en lenguaje natural sobre datos de ventas utilizando OpenAI para convertir preguntas en consultas SQL.

## 🚀 Características

- **API REST** construida con FastAPI
- **Procesamiento de lenguaje natural** con OpenAI GPT para convertir preguntas en SQL
- **Base de datos SQLite** con más de 24,000 registros de ventas
- **Dockerizado** para fácil despliegue
- **CORS habilitado** para integración con frontend
- **Carga automática de datos** desde CSV

## 📊 Datos

El proyecto incluye un dataset de ventas con las siguientes columnas:
- `date` - Fecha de la venta
- `week_day` - Día de la semana
- `hour` - Hora de la venta
- `ticket_number` - Número de ticket
- `waiter` - ID del mesero
- `product_name` - Nombre del producto
- `quantity` - Cantidad vendida
- `unitary_price` - Precio unitario
- `total` - Total de la venta

## 🏗️ Arquitectura

```
app/
├── main.py              # API FastAPI + configuración CORS
├── database.py          # Configuración SQLAlchemy
├── models.py            # Modelos de base de datos
├── services/
│   ├── llm.py          # Integración OpenAI
│   └── query_runner.py # Ejecutor de consultas SQL
└── utils/
    └── csv_loader.py   # Cargador de datos CSV
```

## 🛠️ Tecnologías

- **FastAPI** - Framework web moderno para APIs
- **SQLAlchemy** - ORM para manejo de base de datos
- **OpenAI API** - Procesamiento de lenguaje natural
- **Pandas** - Manipulación de datos
- **Docker** - Contenedorización
- **SQLite** - Base de datos ligera

## ⚡ Inicio Rápido

### Requisitos Previos

- Docker y Docker Compose instalados
- Clave API de OpenAI

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd nivii-challenge-be
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env` y agregar tu clave de OpenAI:

```env
OPENAI_API_KEY=tu_clave_de_openai_aqui
```

### 3. Ejecutar con Docker Compose

```bash
# Construir y ejecutar los contenedores
docker-compose up --build

# O ejecutar en segundo plano (detached mode)
docker-compose up --build -d

# Ver logs en tiempo real (si ejecutaste en modo detached)
docker-compose logs -f
```

La API estará disponible en: `http://localhost:8000`

#### Comandos útiles de Docker Compose

```bash
# Detener los contenedores
docker-compose down

# Reconstruir solo si hay cambios
docker-compose up --build

# Ejecutar en segundo plano
docker-compose up -d

# Ver estado de los contenedores
docker-compose ps

# Ver logs
docker-compose logs backend

# Limpiar todo (contenedores, volúmenes, redes)
docker-compose down --volumes --remove-orphans
```

## 📡 API Endpoints

### POST `/ask`

Realiza una consulta en lenguaje natural sobre los datos de ventas.

**Request:**
```json
{
  "question": "¿Cuáles fueron las ventas totales en noviembre?"
}
```

**Response:**
```json
{
  "sql": "SELECT SUM(total) as ventas_totales FROM sales WHERE date LIKE '11/%/2024'",
  "data": {
    "columns": ["ventas_totales"],
    "rows": [[1250000]]
  }
}
```

### Ejemplos de consultas

- "¿Cuál es el producto más vendido?"
- "¿Cuánto vendió el mesero 51 en octubre?"
- "¿Cuáles son las ventas por día de la semana?"
- "¿Qué productos tienen precio mayor a 20000?"

## 🧪 Pruebas

### Probar la API con curl

```bash
curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"question": "¿Cuántos productos diferentes hay?"}'
```

### Documentación automática

FastAPI genera documentación automática:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🐳 Docker

### Con Docker Compose (Recomendado)

Docker Compose orquesta todos los servicios necesarios automáticamente:

```bash
# Clonar el repositorio
git clone <repository-url>
cd nivii-challenge-be

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu OPENAI_API_KEY

# Construir y ejecutar
docker-compose up --build

# Para ejecutar en segundo plano
docker-compose up --build -d
```

**Configuración en docker-compose.yml:**
```yaml
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data.csv:/app/data.csv
    env_file:
      - .env
```

### Construcción manual

```bash
docker build -t nivii-backend .
docker run -p 8000:8000 --env-file .env nivii-backend
```

### Variables de entorno en Docker

El contenedor lee las variables desde `.env`:

```env
OPENAI_API_KEY=tu_clave_aqui
```

### Troubleshooting Docker

```bash
# Si tienes problemas con permisos o caché
docker-compose down --volumes
docker-compose build --no-cache
docker-compose up

# Ver logs detallados
docker-compose logs -f backend

# Acceder al contenedor para debugging
docker-compose exec backend bash
```

## 🔧 Desarrollo Local

### Sin Docker

1. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

2. **Configurar variables de entorno:**
```bash
export OPENAI_API_KEY=tu_clave_aqui
```

3. **Ejecutar la aplicación:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📁 Estructura de Archivos

```
nivii-challenge-be/
├── app/                     # Código principal
│   ├── main.py             # FastAPI app + CORS
│   ├── database.py         # Configuración DB
│   ├── models.py           # Modelos SQLAlchemy
│   ├── services/           # Lógica de negocio
│   └── utils/              # Utilidades
├── data.csv                # Dataset de ventas (24K+ registros)
├── docker-compose.yml      # Orquestación
├── Dockerfile              # Imagen del backend
├── requirements.txt        # Dependencias Python
├── .env.example           # Plantilla de configuración
└── .gitignore             # Archivos ignorados
```

## 🔒 Seguridad

- **Variables sensibles** en `.env` (excluido de Git)
- **Validación de entrada** con Pydantic
- **Ejecución segura** de consultas SQL
- **CORS configurado** para orígenes específicos

## 🚦 Estados de la API

- `200` - Consulta exitosa
- `500` - Error interno (consulta SQL inválida, error de OpenAI, etc.)

## 🤝 Contribución

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📝 Notas Técnicas

- La base de datos se inicializa automáticamente al iniciar la aplicación
- Los datos se cargan desde `data.csv` en el primer arranque
- OpenAI genera consultas SQL que se ejecutan de forma segura
- El sistema está optimizado para consultas sobre datos de ventas

## 🔗 Enlaces Útiles

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

---

Desarrollado como parte del Nivii Challenge 🚀
