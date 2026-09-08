from typing import Dict, Any
from contextlib import contextmanager
from mysql.connector import Error, pooling



class DAO:
    def __init__(self, config: Dict[str, Any]):
        # Copiamos y ajustamos la configuración
        self.config = config.copy()
        self.config.setdefault('connection_timeout', 8)

        # Configuración del pool (ajusta según tus necesidades)
        pool_config = self.config.copy()
        pool_config.update({
            'pool_name': 'dao_pool',  # nombre único si tienes varios pools
            'pool_size': 1,  # número de conexiones en el pool (ajusta: 5-20 típico)
            'pool_reset_session': True,  # resetea sesión al devolver al pool (recomendado)
            'autocommit': False,  # lo manejamos manualmente
        })

        try:
            self.pool = pooling.MySQLConnectionPool(**pool_config)
            print(f"Connection pool creado: {pool_config['pool_name']} (size: {pool_config['pool_size']})")
        except Error as e:
            print("Error al crear el connection pool")
            # raise ConnectionError(f"No se pudo crear el pool de conexiones: {e}") from e

    # type: ignore
    @contextmanager
    def _get_connection_and_cursor(self):
        """Context manager: obtiene conexión y cursor del pool, maneja commit/rollback y devolución"""
        conn = None
        cursor = None
        try:
            conn = self.pool.get_connection()
            cursor = conn.cursor(dictionary=True)
            yield conn, cursor

            # Si llegamos aquí sin excepción → commit
            conn.commit()
        except Exception as e:
            if conn:
                print(str(e.args))
                conn.rollback()
            raise
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            if conn:
                try:
                    conn.close()  # ← DEVUELVE la conexión al pool (NO la cierra de verdad)
                except:
                    pass

    def close(self):
        """Opcional: no es común cerrar el pool en runtime, pero por si acaso"""
        # En la mayoría de casos NO cierras el pool durante la vida de la app
        # Solo se destruiría al finalizar el proceso
        pass

    def execute_query(self, query: str, params: tuple = None) -> list[Dict]: # type: ignore
        """Consultas de lectura (SELECT)"""
        with self._get_connection_and_cursor() as (conn, cursor):   # type: ignore[call-arg]
            cursor.execute(query, params or ())
            return cursor.fetchall()

    def execute_commit(self, query: str, params: tuple = None) -> int: # type: ignore
        """Operaciones que modifican datos (INSERT, UPDATE, DELETE)"""
        with self._get_connection_and_cursor() as (conn, cursor):   # type: ignore[call-arg]
            cursor.execute(query, params or ())
            return cursor.rowcount

    def execute_insert_get_id(self, query: str, params: tuple = None) -> int: # type: ignore
        """Variante útil para INSERT que devuelve el ID insertado"""
        with self._get_connection_and_cursor() as (conn, cursor):   # type: ignore[call-arg]
            cursor.execute(query, params or ())
            return cursor.lastrowid

    def is_pool_healthy(self) -> bool:
        """Debug: verifica si el pool responde"""
        try:
            with self._get_connection_and_cursor() as (conn, _):    # type: ignore[call-arg]
                return conn.is_connected()
        except:
            return False