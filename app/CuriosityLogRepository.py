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

    def get_recent_user_messages_by_user(self, limit=100):
        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor(dictionary=True)
    
            # 直近100件の中に登場したユーザーIDの取得
            cursor.execute(f"""
                SELECT DISTINCT user_id
                FROM (
                    SELECT user_id
                    FROM curiosity_log
                    ORDER BY id DESC
                    LIMIT {limit}
                ) AS recent_logs;
            """)
            user_ids = [row['user_id'] for row in cursor.fetchall()]
    
            # 結果格納用
            user_messages = {}
    
            for user_id in user_ids:
                cursor.execute("""
                    SELECT message, msg_cate, msg_type
                    FROM curiosity_log
                    WHERE user_id = %s
                    ORDER BY id DESC
                    LIMIT 100
                """, (user_id,))
                user_messages[user_id] = cursor.fetchall()
    
            return user_messages
    
        except mysql.connector.Error as err:
            print(f"[✗] MySQL Error: {err}")
            return {}
        finally:
            if cursor: cursor.close()
            if conn: conn.close()


    def get_latest_messages(self,user_id, limit=100):
        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor(dictionary=True)
    
            query = f"""
                SELECT message FROM curiosity_log
                WHERE message IS NOT NULL AND user_id != %s
                ORDER BY id DESC
                LIMIT {limit}
            """
            cursor.execute(query,(user_id,))
            return [row['message'] for row in cursor.fetchall()]
    
        except mysql.connector.Error as err:
            print(f"[✗] MySQL Error: {err}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def get_latest_my_messages(self,user_id, limit=100):
        conn = None
        cursor = None
        try:
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor(dictionary=True)

            query = f"""
                SELECT message FROM curiosity_log
                WHERE message IS NOT NULL AND user_id = %s
                ORDER BY id DESC
                LIMIT {limit}
            """
            cursor.execute(query,(user_id,))
            return [row['message'] for row in cursor.fetchall()]

        except mysql.connector.Error as err:
            print(f"[✗] MySQL Error: {err}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()    

    def get_latest_messages_joined(self,user_id, limit=100, format: str = "raw") -> str:
        """
        最新のメッセージを1つの文字列として返す。
        format:
            - "bullet": 箇条書き（-）
            - "number": 番号付き
            - "split": セクション区切り（---）
            - "raw": 改行だけ
        """
        messages = self.get_latest_messages(user_id, limit)
    
        if format == "bullet":
            return "\n".join(f"- {msg}" for msg in messages if msg.strip())
        elif format == "number":
            return "\n".join(f"{i+1}. {msg}" for i, msg in enumerate(messages) if msg.strip())
        elif format == "split":
            return "\n---\n".join(msg for msg in messages if msg.strip())
        elif format == "raw":
            return "\n".join(msg for msg in messages if msg.strip())
        else:
            raise ValueError("Unsupported format specified.")

    def get_latest_my_messages_joined(self,user_id, limit=100, format: str = "raw") -> str:
        """
        最新のメッセージを1つの文字列として返す。
        format:
            - "bullet": 箇条書き（-）
            - "number": 番号付き
            - "split": セクション区切り（---）
            - "raw": 改行だけ
        """
        messages = self.get_latest_my_messages(user_id, limit)

        if format == "bullet":
            return "\n".join(f"- {msg}" for msg in messages if msg.strip())
        elif format == "number":
            return "\n".join(f"{i+1}. {msg}" for i, msg in enumerate(messages) if msg.strip())
        elif format == "split":
            return "\n---\n".join(msg for msg in messages if msg.strip())
        elif format == "raw":
            return "\n".join(msg for msg in messages if msg.strip())
        else:
            raise ValueError("Unsupported format specified.")
