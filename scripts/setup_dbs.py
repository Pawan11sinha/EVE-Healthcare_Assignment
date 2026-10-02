import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_db_if_not_exists(dbname):
    try:
        conn = psycopg2.connect(user="postgres", password="password", host="localhost", port="5432")
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{dbname}'")
        exists = cur.fetchone()
        if not exists:
            cur.execute(f"CREATE DATABASE {dbname}")
            print(f"Created database {dbname}")
        else:
            print(f"Database {dbname} already exists")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Failed to create DB {dbname}: {e}")

if __name__ == "__main__":
    create_db_if_not_exists("eve_diagnostics")
    create_db_if_not_exists("eve_diagnostics_test")
