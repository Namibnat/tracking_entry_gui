import json
import os
from contextlib import closing
import datetime

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
    Write a new habit metadata to db.

    sql:
        CREATE TABLE IF NOT EXISTS habit_tracking_types
        (
            id SERIAL PRIMARY KEY,
            title text,
            drop_down_fields jsonb,
            include_notes boolean
        );
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
    try:
        with closing(conn):
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
    except Exception as e:
        print(str(e))
        return False


def add_record(data: dict):
    """
    Add or update a record

    sql:
        CREATE TABLE IF NOT EXISTS habit_tracking_fields (
            id SERIAL PRIMARY KEY,
            entry_date DATE NOT NULL,
            entry_title TEXT NOT NULL,
            outcome_option TEXT,
            notes TEXT,
            UNIQUE (entry_date, entry_title)
        );
    :return: Success status
    :rtype: bool
    """
    conn = make_connection()
    if not conn:
        return False
    try:
        date = data.get('date')
        entry_date = datetime.date(date.year, date.month, date.day)
        entry_title = data.get('entry_title')
        outcome_option = data.get('drop-down')
        notes = data.get('notes', None)
        assert isinstance(entry_title, str)
        assert isinstance(outcome_option, str)
        assert isinstance(notes, str)
    except Exception as e:
        print(str(e))
        return False
    try:
        with closing(conn):
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO habit_tracking_fields (
                        entry_date,
                        entry_title,
                        outcome_option,
                        notes
                        )
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (entry_date, entry_title)
                    DO UPDATE SET
                        outcome_option = EXCLUDED.outcome_option,
                        notes = EXCLUDED.notes;
                    """,
                    (entry_date, entry_title, outcome_option, notes)
                )
                conn.commit()
                return True
    except Exception as e:
        print(str(e))
        return False
