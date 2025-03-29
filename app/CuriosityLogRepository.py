import mysql.connector

class CuriosityLogRepository:
    def __init__(self):
        self.config = {
            'host': 'db',
            'user': 'wiki',
            'password': 'wiki',
            'database': 'wikidb',
            'port': 3306,
            'charset': 'utf8mb4'
        }

    def insert_log(self, user_id, speaker_type, message, msg_cate, msg_type):
        try:
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor()

            query = """
                INSERT INTO curiosity_log (user_id, speaker_type, message, msg_cate, msg_type)
                VALUES (%s, %s, %s, %s, %s)
            """
            values = (user_id, speaker_type, message, msg_cate, msg_type)
            cursor.execute(query, values)
            conn.commit()

            print(f"[✓] Inserted curiosity_log for user_id={user_id}")

        except mysql.connector.Error as err:
            print(f"[✗] MySQL Error: {err}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

