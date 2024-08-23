import string

import psycopg2

class PostgresDict:
    def __init__(self, table_name):
        try:
            self.conn = psycopg2.connect(
                dbname="jobs",
                user="postgres",
                password="",
                host="172.21.12.39",
                port="5432"
            )
            print("Connection successful")
        except psycopg2.OperationalError as e:
            print(f"OperationalError: {e}")

        self.table_name = table_name

    def __getitem__(self, key):
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT company, title FROM {self.table_name} WHERE key = %s", (key,))
            result = cur.fetchone()
            if result is None:
                raise KeyError(key)
            company, title = result
            return JobEntry(title=title, company=company)

    def __setitem__(self, key, value: 'JobEntry'):
        with self.conn.cursor() as cur:
            cur.execute(f"""
            INSERT INTO {self.table_name} (key, company, title)
            VALUES (%s, %s, %s)
            ON CONFLICT (key) DO UPDATE 
            SET company = EXCLUDED.company, title = EXCLUDED.title
            """, (key, value.company, value.title))
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
            cur.execute(f"SELECT key, company, title FROM {self.table_name}")
            return cur.fetchall()

    def close(self):
        self.conn.close()

class JobEntry:
    def __init__(self, company: str, title: str) -> None:
        self.title = title
        self.company = company

class JobFolder:
    def __init__(self) -> None:
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
            job_entry = self.__db[key]
            del self.__db[key]
            self.__db.conn.commit()
            return job_entry
        else:
            return None

    def job_items(self):
        return [(key, value) for key, value in self.__db.items()]

    def close(self) -> None:
        self.__db.close()
