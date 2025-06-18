import contextlib
import psycopg2
import functools
from typing import Tuple,List
from app.core.settings import get_settings
from ..utils.date_util import get_est_time

settings  = get_settings()

def save_doc_type_template(document_id: str, doc_type: str, version: str,
                           country_id: int, doc_text: str, doc_type_code: str):
    current_date = get_est_time()
    with database() as db_connection:
        cursor = db_connection.cursor()
        
        cursor.execute("""
            CALL public.insert_doc_type_template(%s, %s, %s, %s, %s, %s, %s, %s)
        """, (document_id, doc_type, version, True, True, country_id, doc_text, doc_type_code))        
        db_connection.commit()
        cursor.close()    
            
@functools.cache
def get_templates(countryid:int) -> List[Tuple[str, ...]]:
    with database() as db_connection:
        cursor = db_connection.cursor()
        cursor.execute("""
            SELECT id, doc_type, doc_text, doc_type_code FROM public.doc_type_template where country_id = %s
        """,
          (countryid,)
        )
        rows = cursor.fetchall()  # Returns list of tuples
        cursor.close()
        return rows
    

def save_doc_logs(upload_file_id: str, file_name:str,is_processed:bool,doc_type: str,content:str,p_tenant_id:str,load_id=None):
    current_date = get_est_time()
    with database() as db_connection:            
        cursor = db_connection.cursor()        
        cursor.execute("""
            CALL public.insert_doc_log(%s, %s, %s, %s, %s,%s,%s)
        """, (upload_file_id,file_name, is_processed,doc_type, content,p_tenant_id,load_id))        
        db_connection.commit()
        cursor.close()   


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