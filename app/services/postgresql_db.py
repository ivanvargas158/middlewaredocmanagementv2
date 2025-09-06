import contextlib
import psycopg2
import asyncpg
from async_lru import alru_cache
from typing import Optional
from app.core.settings import get_settings
from ..utils.date_util import get_est_time

settings  = get_settings()


# Singleton pool holder
db_pool: Optional[asyncpg.Pool] = None


async def init_db_pool():
    global db_pool
    if db_pool is None:
        db_pool = await asyncpg.create_pool(
            host=settings.postgresql_host,
            database=settings.postgresql_db_name,
            user=settings.postgresql_db_user,
            password=settings.postgresql_db_pwd,
            min_size=1,
            max_size=10,   
        )
    return db_pool

@contextlib.asynccontextmanager
async def database_async():
    global db_pool
    if db_pool is None:
        await init_db_pool()        
    assert db_pool is not None
    async with db_pool.acquire() as conn:
        yield conn


@contextlib.contextmanager
def database():
    conn = psycopg2.connect(
            host=settings.postgresql_host,
            database=settings.postgresql_db_name,
            user=settings.postgresql_db_user,
            password=settings.postgresql_db_pwd,
        )
    yield conn

    conn.close()


async def save_doc_type_template(
    document_id: str, doc_type: str, version: str,
    country_id: int, doc_text: str, doc_type_code: str
):
    current_date = get_est_time()
    async with database_async() as conn:
        await conn.execute("""
            CALL public.insert_doc_type_template($1, $2, $3, $4, $5, $6, $7, $8)
        """, document_id, doc_type, version, True, True, country_id, doc_text, doc_type_code)
            
@alru_cache()
async def get_templates(countryid: int) -> list[tuple[str, str, str, str, bool]]:
    async with database_async() as conn:
        rows = await conn.fetch("""
            SELECT id, doc_type, doc_text, doc_type_code, is_requiered
            FROM public.doc_type_template
            WHERE country_id = $1
        """, countryid)
        return [tuple(row.values()) for row in rows]
    

async def save_doc_logs(file_name: str,notes: str, content: str, doc_id: str):
 
    async with database_async() as conn:
        await conn.execute("""
            CALL public.insert_doc_log($1, $2, $3, $4)
        """, file_name, notes, content, doc_id) 

