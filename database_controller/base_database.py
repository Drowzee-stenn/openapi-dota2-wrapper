import sqlite3


class BaseDatabase:

    def __init__(self, path_to_db: str = None):
        self.database = sqlite3.connect(path_to_db)
        self.cursor = self.database.cursor()

    def execute_and_commit(self, query):
        self.cursor.execute(query)
        self.database.commit()

    def insert_into_table(self, table_name, *values):
        query = f'INSERT INTO {table_name} VALUES {values}'
        self.execute_and_commit(query)

    def select_and_fetchone(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchone()
