

import sqlite3
from typing import Dict, List, Optional


class Database:
    def __init__(self, db_path: str = "university_dating.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT
        )
        """
        )
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS profiles (
            user_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            faculty TEXT NOT NULL,
            course INTEGER NOT NULL,
            bio TEXT NOT NULL,
            photo_id TEXT NOT NULL,
            active INTEGER DEFAULT 1,
            blocked INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        """
        )
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user_id INTEGER NOT NULL,
            to_user_id INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (from_user_id) REFERENCES users (user_id),
            FOREIGN KEY (to_user_id) REFERENCES users (user_id)
        )
        """
        )
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user_id INTEGER NOT NULL,
            to_user_id INTEGER NOT NULL,
            reason TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (from_user_id) REFERENCES users (user_id),
            FOREIGN KEY (to_user_id) REFERENCES users (user_id)
        )
        ''')
        self.conn.commit()

    def add_user(self, user_id: int, username: str, full_name: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)",
            (user_id, username, full_name),
        )
        self.conn.commit()

    def save_profile(self, user_id: int, profile_data: Dict):
        cursor = self.conn.cursor()
        cursor.execute(
            """INSERT OR REPLACE INTO profiles 
            (user_id, name, age, gender, faculty, course, bio, photo_id) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user_id,
                profile_data["name"],
                profile_data["age"],
                profile_data["gender"],
                profile_data["faculty"],
                profile_data["course"],
                profile_data["bio"],
                profile_data["photo_id"],
            ),
        )
        self.conn.commit()

    def get_profile(self, user_id: int) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return {
                "user_id": row[0],
                "name": row[1],
                "age": row[2],
                "gender": row[3],
                "faculty": row[4],
                "course": row[5],
                "bio": row[6],
                "photo_id": row[7],
            }
        return None

    def delete_profile(self, user_id: int):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM profiles WHERE user_id = ?", (user_id,))
        self.conn.commit()

    def set_profile_active(self, user_id: int, active: bool):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE profiles SET active = ? WHERE user_id = ?",
            (1 if active else 0, user_id),
        )
        self.conn.commit()

    def get_all_profiles(self, exclude_user_id: int) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM profiles WHERE user_id != ? AND active = 1",
            (exclude_user_id,),
        )
        rows = cursor.fetchall()
        return [
            {
                "user_id": row[0],
                "name": row[1],
                "age": row[2],
                "gender": row[3],
                "faculty": row[4],
                "course": row[5],
                "bio": row[6],
                "photo_id": row[7],
            }
            for row in rows
        ]

    def migrate_gender_values(self):
        cursor = self.conn.cursor()
        # Все варианты мужского
        cursor.execute(
            "UPDATE profiles SET gender = 'мужской' WHERE LOWER(TRIM(gender)) IN ('мужской', 'мужчина', 'male', 'm', 'парень')"
        )
        # Все варианты женского
        cursor.execute(
            "UPDATE profiles SET gender = 'женский' WHERE LOWER(TRIM(gender)) IN ('женский', 'женщина', 'female', 'f', 'девушка')"
        )
        self.conn.commit()

    def get_profiles_by_gender(self, exclude_user_id: int, gender: str) -> List[Dict]:
        import logging

        cursor = self.conn.cursor()
        gender_param = gender.strip().lower()
        logging.info(f"Поиск по полу: gender_param={gender_param}")
        cursor.execute(
            "SELECT * FROM profiles WHERE user_id != ? AND LOWER(TRIM(gender)) = ? AND active = 1",
            (exclude_user_id, gender_param),
        )
        rows = cursor.fetchall()
        logging.info(f"Найдено анкет: {len(rows)}")
        return [
            {
                "user_id": row[0],
                "name": row[1],
                "age": row[2],
                "gender": row[3],
                "faculty": row[4],
                "course": row[5],
                "bio": row[6],
                "photo_id": row[7],
            }
            for row in rows
        ]

    def add_like(self, from_user_id: int, to_user_id: int):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO likes (from_user_id, to_user_id) VALUES (?, ?)",
            (from_user_id, to_user_id),
        )
        self.conn.commit()

    def add_complaint(self, from_user_id: int, to_user_id: int, reason: str = ""):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO complaints (from_user_id, to_user_id, reason) VALUES (?, ?, ?)',
            (from_user_id, to_user_id, reason)
        )
        self.conn.commit()

    def get_complaints_count(self, to_user_id: int) -> int:
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM complaints WHERE to_user_id = ?', (to_user_id,))
        return cursor.fetchone()[0]

    def block_user(self, user_id: int):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE profiles SET blocked = 1, active = 0 WHERE user_id = ?', (user_id,))
        self.conn.commit()

    def unblock_user(self, user_id: int):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE profiles SET blocked = 0, active = 1 WHERE user_id = ?', (user_id,))
        self.conn.commit()

    def is_user_blocked(self, user_id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute('SELECT blocked FROM profiles WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        return bool(row and row[0])

    def get_total_users(self) -> int:
        """Возвращает общее количество пользователей"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        return cursor.fetchone()[0]

    def get_total_profiles(self) -> int:
        """Возвращает общее количество анкет"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM profiles")
        return cursor.fetchone()[0]

    def get_active_profiles_count(self) -> int:
        """Возвращает количество активных анкет"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM profiles WHERE active = 1")
        return cursor.fetchone()[0]

    def get_mutual_likes(self, user_id: int) -> List[Dict]:
        """Возвращает взаимные лайки (матчи) для пользователя"""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT DISTINCT p.* 
            FROM profiles p
            INNER JOIN likes l1 ON p.user_id = l1.to_user_id AND l1.from_user_id = ?
            INNER JOIN likes l2 ON p.user_id = l2.from_user_id AND l2.to_user_id = ?
            WHERE p.active = 1
        """,
            (user_id, user_id),
        )
        rows = cursor.fetchall()
        return [
            {
                "user_id": row[0],
                "name": row[1],
                "age": row[2],
                "gender": row[3],
                "faculty": row[4],
                "course": row[5],
                "bio": row[6],
                "photo_id": row[7],
            }
            for row in rows
        ]

    def get_user_likes_count(self, user_id: int) -> int:
        """Возвращает количество лайков, которые поставил пользователь"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM likes WHERE from_user_id = ?", (user_id,))
        return cursor.fetchone()[0]

    def get_user_likes_received_count(self, user_id: int) -> int:
        """Возвращает количество лайков, которые получил пользователь"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM likes WHERE to_user_id = ?", (user_id,))
        return cursor.fetchone()[0]

    def close(self):
        self.conn.close()
