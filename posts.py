import sqlite3 as sql
import os
from flask import redirect

# save new post to database
def savepost(name,request,aktualni_adresar):
        dotaz = request.form['dotaz']
        kategorie = request.form['kategorie']
        anonym = request.form['anonymita']
        con = sql.connect(os.path.join(aktualni_adresar, 'main.db'))
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('SELECT email, jmeno, prijmeni FROM uzivatele WHERE uzivatel = ?', [name])
        rows = cur.fetchall()
        con.commit()
        con.close()
        for row in rows:
            mail = row['email']
            jmeno = row['jmeno']
            prijmeni = row['prijmeni']
        email = mail
        j = jmeno
        p = prijmeni

        if anonym == "ano":
            jj = "Anonymní"
            pp = "příspěvek"
            con = sql.connect(os.path.join(aktualni_adresar, 'main.db'))
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute('INSERT INTO dotazy (email, kategorie, dotaz, jmeno, prijmeni)  VALUES (?, ?, ?, ?, ?);', [email, kategorie, dotaz, jj, pp])
            con.commit()
            con.close()
            return "1"
        else:
            con = sql.connect(os.path.join(aktualni_adresar, 'main.db'))
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute('INSERT INTO dotazy (email, kategorie, dotaz, jmeno, prijmeni)  VALUES (?, ?, ?, ?, ?);', [email, kategorie, dotaz, j, p])
            con.commit()
            con.close()
            return "1"
