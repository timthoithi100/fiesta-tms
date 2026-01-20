from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings
import redis.asyncio as aioredis
from typing import AsyncGenerator

# SQLAlchemy Base
Base = declarative_base()

# Create async engine
engine = create_async_engine(
    settings.database_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_pre_ping=True,
    echo=settings.debug,
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Redis connection pool
redis_pool = None


async def get_redis_pool():
    global redis_pool
    if redis_pool is None:
        redis_pool = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=10
        )
    return redis_pool


async def close_redis_pool():
    global redis_pool
    if redis_pool:
        await redis_pool.close()
        redis_pool = None


# Dependency for getting database session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Dependency for getting Redis connection
async def get_redis():
    pool = await get_redis_pool()
    return pool


# Initialize database tables
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Close database connections
async def close_db():
    await engine.dispose()
    await close_redis_pool()