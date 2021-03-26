#encoding: utf-8
from flask import Flask, render_template, redirect, request, url_for, session, escape
import sqlite3 as sql
import verify
import datetime
import os
import posts


app = Flask(__name__)
app.secret_key = "2bcjhcebcjec35hjhh605"
app.debug = True

aktualni_adresar = os.path.abspath(os.path.dirname(__file__))
now = datetime.datetime.now()

@app.context_processor
def inject_user():
    if not session.get('username'):
        return dict(perms=0)
    else:
        user = session['username']
        perms = verify.permissions(user,aktualni_adresar)
        return dict(perms=perms,usr=user)

@app.route('/')
def index():
    if not session.get('username'):
        return render_template('index.html', usr="nic")
    else:   
        LastEvent = NejblizsiUdalost()
        return render_template('index.html', event=LastEvent)

@app.route('/action/newuser')
def registrace():
    return render_template('registrace.html')

@app.route('/back/deletep:<rowid>', methods=["GET"])
def deletepost(rowid):
        name = session['username']
        con = sql.connect(os.path.join(aktualni_adresar, 'main.db'))
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('SELECT * FROM uzivatele WHERE uzivatel = ?;', [name])
        rows = cur.fetchall()
        con.commit()
        con.close()
        for row in rows:
            role = row['role']
        if role == "SUPERUSER":
            con = sql.connect(os.path.join(aktualni_adresar, 'main.db'))
            con.row_factory = sql.Row
            cur = con.cursor()
            idecko = rowid
            cur.execute('DELETE FROM dotazy WHERE ROWID = ?;', [idecko])
            con.commit()
            con.close()
            return redirect('/')
        else:
            return("Přístup odepřen, běž si hrát na hřiště :)")



@app.route('/back/newuser', methods=["POST"])
def newuser():
        jmeno = request.form['first_name']
        prijmeni = request.form['last_name']
        email = request.form['email']
        heslo = request.form['password']
        nickname = request.form['nickname']
        verifyEmail = verify.verify_mail(email)
        if verifyEmail == "ok":
            con = sql.connect(os.path.join(aktualni_adresar, 'main.db'))
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute('INSERT INTO uzivatele (uzivatel, heslo, email, jmeno, prijmeni)  VALUES (?, ?, ?, ?, ?);', [nickname, heslo, email, jmeno, prijmeni])
            con.commit()
            con.close()
            return redirect('/back/logout')
        else:
            return("Zadaný email nepochází z domény @decathlon.com")

@app.route('/novyp')
def newquestion():
    return render_template('dotaz.html')

@app.route('/novau')
def newevent():
    return render_template('novaudalost.html')

@app.route('/prehled')
def prehled():
    user = session['username']
    con = sql.connect(os.path.join(aktualni_adresar, 'main.db'))
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('SELECT *, ROWID FROM dotazy ORDER BY vlozeno DESC, vcase DESC;')
    posts = cur.fetchall()
    return render_template('vypis.html', rows=posts)

@app.route('/prehled:<kategorie>')
def prehledby(kategorie):
    con = sql.connect(os.path.join(aktualni_adresar, 'main.db'))
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('SELECT *, ROWID FROM dotazy WHERE kategorie = ?;', [kategorie])
    rows = cur.fetchall()
    return render_template('vypis.html', rows=rows)

@app.route('/back/newevent', methods=['POST'])
def saveevent():
        name = session['username']
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
        nazev = request.form['nazev_udalosti']
        popis = request.form['popis_udalosti']
        datum = request.form['datum_udalosti']
        cas = request.form['cas_udalosti']
        con = sql.connect(os.path.join(aktualni_adresar, 'main.db'))
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute('INSERT INTO udalosti (email, jmeno, prijmeni, nazev, popis, datum, cas)  VALUES (?, ?, ?, ?, ?, ?, ?);', [email, j, p, nazev, popis, datum, cas])
        con.commit()
        con.close()
        return redirect('/')

@app.route('/back/newpost', methods=['POST'])
def Do_savepost():
        name = session['username']
        if posts.savepost(name,request,aktualni_adresar) == "1":
            return redirect("/prehled")

# overovani uzivatele
@app.route('/back/auth', methods=['POST'])
def auth():
    name = request.form['jmeno']
    heslo = request.form['heslo']
    vysledek = overeni(name, heslo)
    if vysledek != "neni":
        session['username'] = request.form['jmeno']
        session['logged in'] = True
        return redirect("/")
    else:
        return("Špatné heslo/jméno")

# vypise komentare dle id příspěvku
@app.route('/komentare:<postid>', methods=['GET'])
def vypiskomentaru(postid):
    con = sql.connect(os.path.join(aktualni_adresar, 'main.db'))
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('SELECT * FROM komentare WHERE postID = ?;', [postid])
    rows = cur.fetchall()

    return render_template('komentare.html', rows=rows, row=postid)

# vypise detail udalosti dle jejiho id
@app.route('/udalost:<eventid>', methods=['GET'])
def vypisjedneudalosti(eventid):
    con = sql.connect(os.path.join(aktualni_adresar, 'main.db'))
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('SELECT * FROM udalosti WHERE ROWID = ?;', [eventid])
    rows = cur.fetchall()

    return render_template('udalost.html', rows=rows)

# seznam udalosti
@app.route('/udalosti')
def vypisudalosti():
    con = sql.connect(os.path.join(aktualni_adresar, 'main.db'))
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('SELECT *, ROWID FROM udalosti ORDER BY datum ASC;')
    rows = cur.fetchall()

    return render_template('udalosti.html', rows=rows)

@app.route('/back/comment:<postid>', methods=['POST'])
def poslikometar(postid):
    postID = postid
    komentar = request.form['komentar']
    name = session['username']
    con = sql.connect(os.path.join(aktualni_adresar, 'main.db'))
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('SELECT email, jmeno, prijmeni FROM uzivatele WHERE uzivatel = ?', [name])
    rows = cur.fetchall()
    for row in rows:  
        mail = row['email']
        jmeno = row['jmeno']
        prijmeni = row['prijmeni']
    email = mail
    j = jmeno
    p = prijmeni
    con = sql.connect(os.path.join(aktualni_adresar, 'main.db'))
    cur = con.cursor()
    cur.execute('INSERT INTO komentare (postID, komentar, email, jmeno, prijmeni)  VALUES (?, ?, ?, ?, ?);', [postID, komentar, email, j, p])
    con.commit()
    con.close()
    con = sql.connect(os.path.join(aktualni_adresar, 'main.db'))
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('SELECT * FROM komentare WHERE postID = ?;', [postid])
    rows = cur.fetchall()
    return render_template('komentare.html', rows=rows, row=postid)

def overeni(name, heslo):
    con = sql.connect(os.path.join(aktualni_adresar, 'main.db'))
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('SELECT ROWID FROM uzivatele WHERE uzivatel=? AND heslo=?', [name, heslo])
    if cur.fetchall():
        return("je")
    else:
        return("neni")
# konec overovani

def NejblizsiUdalost():
    con = sql.connect(os.path.join(aktualni_adresar, 'main.db'))
    con.row_factory = sql.Row
    cur = con.cursor()
    dnes = now.strftime("%Y-%m-%d")
    cur.execute('SELECT *, ROWID FROM udalosti WHERE datum < ? ORDER BY datum DESC LIMIT 1;', [dnes])
    rows = cur.fetchall()
    return(rows)

def NajdiJmeno(email):
    con = sql.connect(os.path.join(aktualni_adresar, 'main.db'))
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('SELECT jmeno FROM uzivatele WHERE email = ?', [email])
    rows = cur.fetchall()

    for row in rows:
        j = row

    return(j[0])


@app.route('/back/logout')
def logout():
    session['logged in'] = False
    session.pop('username', None)
    return redirect('/')




if __name__ == '__main__':
    app.run()