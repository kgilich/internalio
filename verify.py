import sqlite3 as sql
import datetime
import os

def verify_mail(email):
    if not "@" in email:
        return "chyba"
    else:
        return "ok"


def permissions(user,aktualni_adresar):
    con = sql.connect(os.path.join(aktualni_adresar, 'main.db'))
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('SELECT * FROM uzivatele WHERE uzivatel = ?;', [user])
    rows = cur.fetchall()
    for row in rows:
        if row['role'] == "SUPERUSER":
            return "SUPERUSER"
        else:
            return "nečum"
