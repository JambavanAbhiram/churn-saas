from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from backend.core.config import get_settings

_engine = None
_SessionLocal = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = create_async_engine(get_settings().DATABASE_URL, echo=False)
    return _engine

def get_session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = async_sessionmaker(get_engine(), expire_on_commit=False)
    return _SessionLocal

async def get_db():
    async with get_session_factory()() as session:
        yield session

async def init_db():
    from backend.db.models import Base
    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
