import json
import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_HOST = os.getenv('POSTGRES_HOST')


def make_connection():
    """
    Make a database connection.

    :return: connection
    :rtype: psycopg2.extensions.connection
    """
    try:
        connection = psycopg2.connect(
            host=POSTGRES_HOST,
            database=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            port=POSTGRES_PORT
        )
        return connection
    except Exception as e:
        print(str(e))
        return False


def write_new_tracking_type(data: dict):
    """
    Write a new habit meta data to db.

            self.new_field_values['title'] = title
        drop_down_values = [v.get() for v in self.drop_down_str_values if v]
        self.new_field_values['drop-down'] = drop_down_values
        self.new_field_values['note'] = self.notes_selected.get()
    :param data:
    :return:
    """
    conn = make_connection()
    if not conn:
        return False

    try:
        title = data.get('title')
        drop_down_values = data.get('drop-down')
        include_notes = data.get('note')
        assert isinstance(title, str)
        assert isinstance(drop_down_values, list)
        assert isinstance(include_notes, bool)
    except Exception as e:
        print(str(e))
        return False
    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO habit_tracking_types (
                title,
                drop_down_fields,
                include_notes
                )
            VALUES (%s, %s, %s);
            """,
            (title, json.dumps(drop_down_values), include_notes)
        )
    conn.commit()
    return True
