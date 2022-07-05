import time
import sqlite3


class Schema():
    USERS_TABLE = "users"
    GISTS_TABLE = "gists"
    ACTIVITY_TABLE = "activity"

    def __init__(self):
        pass

    def createUserTable(self):
        create_query = """CREATE TABLE IF NOT EXISTS %s
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            github_user_id INTEGER (11) NOT NULL,
            username VARCHAR(70) NOT NULL,
            html_url VARCHAR(200),
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
        """ % self.USERS_TABLE
        return create_query


    def createGistsTable(self):
        create_query = """CREATE TABLE IF NOT EXISTS %s
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id VARCHAR (11) NOT NULL,
            gist_url TEXT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
        """ % self.GISTS_TABLE
        return create_query

    def createActivityTable(self):
        create_query = """CREATE TABLE IF NOT EXISTS %s
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id VARCHAR (11) NOT NULL,
            gist_url TEXT,
            activity_id TEXT NOT NULL,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
        """ % self.ACTIVITY_TABLE
        return create_query


class Sqlite(Schema):
    def __init__(self, source_file):
        super().__init__()

        while True:
            try:
                self.connection = sqlite3.connect(source_file, check_same_thread=False)
                self.cursor_ = self.connection.cursor()
                break
            except:
                print("DB Connection error...")
                time.sleep(2)

        # sqlite3.register_adapter(uuid.UUID, lambda u: u.bytes_le)
        # sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))

    def query(self, query, *args):
        self.cursor_.execute(query, args)

    def query_insert(self, table_name, sql_data):
        main_var = ""
        for one in sql_data:
            main_var += "?,"
        main_var = main_var[:-1]

        sql = '''INSERT INTO `{0}` VALUES (NULL, {1})'''.format(table_name, main_var)
        print(sql)
        self.cursor_.execute(sql, sql_data)

    def fetchAll(self):
        results = self.cursor_.fetchall()  # tuple
        return results

    def fetchOne(self):
        result = self.cursor_.fetchone()
        return result

    def close(self):
        self.cursor_.connection.close()

    def commit(self):
        self.connection.commit()


if __name__ == '__main__':
    db = Sqlite("devOps_challenge.db")
    db.query(db.createUserTable())

