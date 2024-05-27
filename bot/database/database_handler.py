from psycopg2 import sql
from datetime import datetime, timedelta, timezone


class DatabaseHandler:
    def __init__(self, connection):
        """A class for handling PostgreSQL database operations."""
        self.connection = connection

    def get_total_rows(self) -> int:
        """Query how many users are in the database."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        total_rows = cursor.fetchone()[0]
        cursor.close()

        return total_rows

    def add_user(self, user_id: str | int):
        """Add a new user to the database with the end of subscription time +7 days from current moment (UTC time)."""
        current_utc_time = datetime.now(timezone.utc)
        subscription_start_string = current_utc_time.strftime("%Y-%m-%d %H:%M:%S")

        subscription_end = current_utc_time + timedelta(days=7)
        subscription_end_string = subscription_end.strftime("%Y-%m-%d %H:%M:%S")

        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO users (user_id, sign_up_date, subscription_end) VALUES (%s, %s, %s)",
                       (user_id, subscription_start_string, subscription_end_string))
        self.connection.commit()

        cursor.execute("INSERT INTO vocabulary (user_id) VALUES (%s)", (user_id,))
        self.connection.commit()
        cursor.close()

    def change_column_value(self, user_id: str | int, table: str, column_name: str, new_value: str | int):
        """Change column value for a user."""
        cursor = self.connection.cursor()
        cursor.execute(sql.SQL("UPDATE {} SET {} = %s WHERE user_id = %s").format(
            sql.Identifier(table), sql.Identifier(column_name)), (new_value, user_id))
        self.connection.commit()
        cursor.close()

    def check_user_exists(self, user_id: str | int) -> bool:
        """Check if user_id exists in the database."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE user_id = %s)", (user_id,))
        exists = cursor.fetchone()[0]
        cursor.close()

        return bool(exists)

    def get_user_column_data(self, user_id: str | int, column_name: str) -> str:
        """Query single column from table 'users' for a user."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT {} FROM users WHERE user_id = %s".format(column_name), (user_id,))
        result = cursor.fetchone()
        cursor.close()

        if result:
            return result[0]
        else:
            return ""

    def get_user_data(self, user_id: str | int) -> dict[str, str]:
        """Query all columns from table 'users' for a user."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        row = cursor.fetchone()
        cursor.close()

        if row:
            column_names = [description[0] for description in cursor.description]
            return {column_names[i]: row[i] for i in range(len(column_names))}
        else:
            return {}

    def get_active_users(self) -> list[dict[str, str]]:
        """Query all users whose status is 'activated'."""
        cursor = self.connection.cursor()
        cursor.execute("SELECT user_id, subscription_end FROM users WHERE status = 1")
        rows = cursor.fetchall()
        cursor.close()

        result = [{'user_id': row[0], 'subscription_end': row[1]} for row in rows]

        return result

    def register_new_item(self, user_id: str | int, column_name: str, new_item: str):
        """Register new item (word or idiom) in a respective column for a user."""
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT {column_name} FROM vocabulary WHERE user_id = %s", (user_id,))
        existing_words = cursor.fetchone()[0]

        if existing_words:
            updated_words = f"{existing_words}|{new_item.lower()}"
        else:
            updated_words = new_item.lower()

        cursor.execute(f"UPDATE vocabulary SET {column_name} = %s WHERE user_id = %s", (updated_words, user_id))
        self.connection.commit()

        cursor.close()

    def check_word_exists_in_column(self, user_id: str | int, column_name: str, item: str) -> bool:
        """Check if an item (word or idiom) is already stored in a respective column for a user."""
        cursor = self.connection.cursor()
        query = f"SELECT COUNT(*) FROM vocabulary WHERE user_id = %s AND {column_name} LIKE %s"

        cursor.execute(query, (user_id, '%' + item.lower() + '%'))

        result = cursor.fetchone()[0]
        cursor.close()

        return result > 0

    def get_last_word_idiom(self, user_id: str) -> list[str]:
        """Query last word and idiom stored for a user."""
        last_items: list[str] = list()
        cursor = self.connection.cursor()

        for item in ['word', 'idiom']:

            cursor.execute(f"SELECT {item} FROM vocabulary WHERE user_id = %s", (user_id,))
            existing_items = cursor.fetchone()[0]

            if existing_items:
                last = existing_items.split('|')[-1]
                last_items.append(last)

        cursor.close()

        return last_items

    def get_user_all_items(self, user_id: str | int, item: str) -> str:
        """Query all items (words or idioms) stored sor a user."""
        existing_items: str
        cursor = self.connection.cursor()

        cursor.execute(f"SELECT {item} FROM vocabulary WHERE user_id = %s", (user_id,))
        existing_items = cursor.fetchone()[0]

        cursor.close()
        return existing_items

    def plus_minus_points(self, user_id: str | int, points: int) -> bool:
        """Adjust user's points if they've earned points or if a deduction won't reduce their total below zero."""
        current_points: int = int(self.get_user_column_data(user_id, 'points'))

        if current_points > 0 or points > 0:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE users SET points = points + %s WHERE user_id = %s", (points, user_id))
            self.connection.commit()
            cursor.close()
            return True

        return False

    def increment_user_checks(self, user_id: str | int):
        """Increase user's amount of daily available checks by 1."""
        cursor = self.connection.cursor()
        cursor.execute("UPDATE users SET checks = checks + 1 WHERE user_id = %s", (user_id,))
        self.connection.commit()
        cursor.close()

    def daily_user_reset(self, user_id: str | int):
        """Reset user's parameters before daily message with new vocabulary."""
        cursor = self.connection.cursor()
        cursor.execute("UPDATE users SET checks = 0, day_word = 0, day_idiom = 0 WHERE user_id = %s", (user_id,))
        self.connection.commit()
        cursor.close()
