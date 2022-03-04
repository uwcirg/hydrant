"""Module to encapsulate extracting KeyCloak event log data"""
import datetime
from flask import current_app
import json
import psycopg2


def get_con():
    """Return live DB connection"""
    return psycopg2.connect(
        dbname=current_app.config.get("DB_DATABASE"),
        user=current_app.config.get("DB_USER"),
        password=current_app.config.get("DB_PASSWORD"),
        host=current_app.config.get("DB_ADDR"),
        port=current_app.config.get("DB_PORT")
    )


def get_count(db_con):
    with db_con.cursor() as cursor:
        cursor.execute("SELECT count(*) FROM event_entity")
        row = cursor.fetchone()
    return row[0]


def user_id_name_map(db_con):
    """Only login events include username - capture mapping"""
    user_ids = []
    with db_con.cursor() as cursor:
        cursor.execute(
            "SELECT DISTINCT(user_id) FROM event_entity")
        for row in cursor:
            if not row[0]:
                continue
            user_ids.append(row[0])

    map = {}
    with db_con.cursor() as cursor:
        for user_id in user_ids:
            cursor.execute(
                "SELECT details_json FROM event_entity "
                f" WHERE type = 'LOGIN' AND user_id = '{user_id}' LIMIT 1")
            row = cursor.fetchone()
            if row:
                map[user_id] = json.loads(row[0]).get("username", "")

    return map


def get_events(db_con):
    user_name_map = user_id_name_map(db_con)
    with db_con.cursor() as cursor:
        cursor.execute(
            "SELECT user_id, session_id, event_time, type, details_json "
            " FROM event_entity LIMIT 20")
        for row in cursor:
            yield {
                "user_id": row[0],
                "user_name": user_name_map.get(row[0], ""),
                "session_id": row[1],
                "event_time": datetime.datetime.fromtimestamp(row[2]/1000).isoformat(),
                "type": row[3],
                "details": json.loads(row[4]),
            }


def dump_events():
    con = get_con()
    results = []
    for event in get_events(con):
        results.append(event)

    return results
