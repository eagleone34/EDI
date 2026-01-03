import json
from typing import Optional
from app.db import get_db_connection, get_cursor
from app.schemas.layout import LayoutConfig

class LayoutService:
    @staticmethod
    def get_active_layout(transaction_type_code: str, user_id: Optional[str] = None) -> Optional[LayoutConfig]:
        """
        Fetch the active layout configuration for a transaction type.
        
        Priority:
        1. If user_id provided and user has a PRODUCTION layout, use that
        2. Otherwise, use the SYSTEM layout (user_id IS NULL)
        
        Returns None if no active layout is found.
        """
        conn = None
        try:
            conn = get_db_connection()
            cur = get_cursor(conn)
            
            config_json = None
            
            # If user_id provided, first try to get user's personal layout
            if user_id:
                cur.execute("""
                    SELECT config_json 
                    FROM layout_versions 
                    WHERE transaction_type_code = %s 
                      AND user_id = %s
                      AND status = 'PRODUCTION'
                      AND is_active = true
                    ORDER BY version_number DESC
                    LIMIT 1;
                """, (transaction_type_code, user_id))
                result = cur.fetchone()
                if result and result.get('config_json'):
                    config_json = result['config_json']
            
            # Fallback to SYSTEM layout if no user layout found (or no user_id provided)
            if not config_json:
                cur.execute("""
                    SELECT config_json 
                    FROM layout_versions 
                    WHERE transaction_type_code = %s 
                      AND user_id IS NULL
                      AND status = 'PRODUCTION'
                      AND is_active = true
                    ORDER BY version_number DESC
                    LIMIT 1;
                """, (transaction_type_code,))
                result = cur.fetchone()
                if result and result.get('config_json'):
                    config_json = result['config_json']
            
            if config_json:
                return LayoutConfig(**config_json)
                
            return None
            
        except Exception as e:
            print(f"Error fetching layout for {transaction_type_code}: {e}")
            return None
        finally:
            if conn:
                conn.close()


    @staticmethod
    def create_initial_layout(transaction_type_code: str, config: LayoutConfig, user_id: str = "system"):
        """Create a new initial layout version."""
        conn = None
        try:
            conn = get_db_connection()
            cur = get_cursor(conn)
            
            query = """
                INSERT INTO layout_versions 
                (transaction_type_code, version_number, status, config_json, is_active, created_by)
                VALUES (%s, 1, 'PRODUCTION', %s, true, %s)
                RETURNING id;
            """
            cur.execute(query, (
                transaction_type_code, 
                json.dumps(config.model_dump()), 
                user_id
            ))
            conn.commit()
            return cur.fetchone()['id']
            
        except Exception as e:
            print(f"Error creating layout: {e}")
            return None
        finally:
            if conn:
                conn.close()
