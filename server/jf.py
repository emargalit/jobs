import psycopg2

class PostgresDict:
    def __init__(self, table_name):
        try:
            self.conn = psycopg2.connect(
                dbname="jobs",
                user="postgres",
                password="",
                host="",
                port="5432"
            )
            print("Connection successful")
        except psycopg2.OperationalError as e:
            print(f"OperationalError: {e}")

        self.table_name = table_name

    def __getitem__(self, key):
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {self.table_name} WHERE key = %s", (key,))
            result = cur.fetchone()
            if result is None:
                raise KeyError(key)
            return result

    def __setitem__(self, key, value):
        with self.conn.cursor() as cur:
            cur.execute(f"""
            INSERT INTO {self.table_name} (key, value)
            VALUES (%s, %s)
            ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
            """, (key, value))
            self.conn.commit()

    def __delitem__(self, key):
        with self.conn.cursor() as cur:
            cur.execute(f"DELETE FROM {self.table_name} WHERE key = %s", (key,))
            self.conn.commit()

    def __contains__(self, key):
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT 1 FROM {self.table_name} WHERE key = %s", (key,))
            return cur.fetchone() is not None

    def items(self):
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT key, value FROM {self.table_name}")
            return cur.fetchall()

    def close(self):
        self.conn.close()

class JobEntry:
    def __init__(self, title: str, company: str) -> None:
        self.title = title
        self.company = company

class JobFolder:
    def __init__(self, source="finance_jobs.sqlite") -> None:
        self.__db = PostgresDict('finance_jobs')

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback) -> None:
        self.close()

    def put(self, key: int, value: JobEntry) -> bool:
        self.__db[key] = value
        self.__db.conn.commit()
        return True

    def get(self, key: str) -> JobEntry or None:
        if key in self.__db:
            return self.__db[key]
        else:
            return None

    def remove(self, key: str) -> JobEntry or None:
        if key in self.__db:
            value = self.__db[key]
            del self.__db[key]
            self.__db.conn.commit()
            return value
        else:
            return None

    def job_items(self):
        return [(key, value) for key, value in self.__db.items()]

    def close(self) -> None:
        self.__db.close()
