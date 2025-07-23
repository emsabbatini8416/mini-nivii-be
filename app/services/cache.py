"""
Cache service for scalability with Redis and memory fallback.
Solves the problem of multiple concurrent users.
"""
import json
import hashlib
import logging
from typing import Any, Optional, Dict
from functools import wraps
import asyncio
import os

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)

class CacheService:
    """Scalable cache service with Redis primary and memory as fallback."""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.memory_cache: Dict[str, Any] = {}
        self.redis_available = False
        
    async def initialize(self):
        """Initializes Redis connection if available."""
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available, using memory cache")
            return
            
        try:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
            self.redis_client = redis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_keepalive=True,
                socket_keepalive_options={},
                health_check_interval=30,
                retry_on_timeout=True,
                retry_on_error=[
                    redis.BusyLoadingError,
                    redis.ConnectionError,
                    redis.TimeoutError
                ]
            )
            
            # Test connection
            await self.redis_client.ping()
            self.redis_available = True
            logger.info("Redis cache initialized successfully")
            
        except Exception as e:
            logger.warning(f"Could not connect to Redis: {e}, using memory cache")
            self.redis_client = None
            self.redis_available = False
    
    def _generate_key(self, prefix: str, data: Any) -> str:
        """Generates a unique key for the cache."""
        data_str = json.dumps(data, sort_keys=True, default=str)
        hash_obj = hashlib.md5(data_str.encode())
        return f"{prefix}:{hash_obj.hexdigest()}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Gets a value from the cache."""
        try:
            if self.redis_available and self.redis_client:
                value = await self.redis_client.get(key)
                if value:
                    return json.loads(value)
            
            # Fallback a memoria
            return self.memory_cache.get(key)
            
        except Exception as e:
            logger.error(f"Error obteniendo del cache: {e}")
            return self.memory_cache.get(key)
    
    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Guarda un valor en el cache."""
        try:
            json_value = json.dumps(value, default=str)
            
            if self.redis_available and self.redis_client:
                await self.redis_client.setex(key, ttl, json_value)
                
            # También guardar en memoria como backup
            self.memory_cache[key] = value
            
            # Limpiar memoria si crece mucho (para escalabilidad)
            if len(self.memory_cache) > 1000:
                # Mantener solo los últimos 500 elementos
                items = list(self.memory_cache.items())
                self.memory_cache = dict(items[-500:])
                
            return True
            
        except Exception as e:
            logger.error(f"Error guardando en cache: {e}")
            # Al menos guardar en memoria
            self.memory_cache[key] = value
            return False
    
    async def delete(self, key: str) -> bool:
        """Elimina una key del cache."""
        try:
            if self.redis_available and self.redis_client:
                await self.redis_client.delete(key)
                
            if key in self.memory_cache:
                del self.memory_cache[key]
                
            return True
            
        except Exception as e:
            logger.error(f"Error eliminando del cache: {e}")
            return False
    
    async def clear(self) -> bool:
        """Limpia todo el cache."""
        try:
            if self.redis_available and self.redis_client:
                await self.redis_client.flushdb()
                
            self.memory_cache.clear()
            return True
            
        except Exception as e:
            logger.error(f"Error limpiando cache: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del cache."""
        stats = {
            'redis_available': self.redis_available,
            'memory_cache_size': len(self.memory_cache)
        }
        
        if self.redis_available and self.redis_client:
            try:
                info = await self.redis_client.info()
                stats.update({
                    'redis_connected_clients': info.get('connected_clients', 0),
                    'redis_used_memory': info.get('used_memory_human', 'N/A'),
                    'redis_hits': info.get('keyspace_hits', 0),
                    'redis_misses': info.get('keyspace_misses', 0)
                })
            except Exception as e:
                logger.error(f"Error obteniendo stats de Redis: {e}")
                
        return stats
    
    async def close(self):
        """Cierra las conexiones del cache."""
        if self.redis_client:
            await self.redis_client.close()

# Instancia global del cache
cache_service = CacheService()

def cache_result(prefix: str = "query", ttl: int = 300):
    """Decorador para cachear resultados de funciones."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generar key del cache
            cache_key = cache_service._generate_key(prefix, {
                'args': args,
                'kwargs': kwargs,
                'function': func.__name__
            })
            
            # Intentar obtener del cache
            cached_result = await cache_service.get(cache_key)
            if cached_result is not None:
                logger.info(f"Cache hit para {func.__name__}")
                return cached_result
            
            # Ejecutar función y cachear resultado
            logger.info(f"Cache miss para {func.__name__}, ejecutando...")
            try:
                result = await func(*args, **kwargs)
                await cache_service.set(cache_key, result, ttl)
                return result
            except Exception as e:
                logger.error(f"Error en función cacheada {func.__name__}: {e}")
                raise
                
        return wrapper
    return decorator

async def init_cache():
    """Inicializa el servicio de cache."""
    await cache_service.initialize()

async def cleanup_cache():
    """Limpia y cierra el servicio de cache."""
    await cache_service.close()
