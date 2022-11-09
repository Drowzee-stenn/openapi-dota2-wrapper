from database_controller.base_database import BaseDatabase


class Database(BaseDatabase):

    def __init__(self):
        super().__init__(path_to_db='resources\\application\\database.db')
        self.create_tables()

    def create_tables(self):
        with open('database_controller\\tables') as file:
            list_of_tables = file.readlines()
        for table in list_of_tables:
            self.execute_and_commit(table)

    def check_match_existence(self, match_id):
        return self.select_and_fetchone(f'SELECT * FROM parsed_matches_history WHERE match_id = {match_id}')
