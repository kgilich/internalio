from flask import Flask, render_template, redirect, request, url_for, session, escape
import sqlite3 as sql
from flask_mail import Mail, Message
import os
import verify


app = Flask(__name__)
app.debug = True
app.secret_key = '2bcjhcebcjec35hjhh605'

mail_settings = {
    "MAIL_SERVER": 'smtp.seznam.cz',
    "MAIL_PORT": '465',
    "MAIL_USE_SSL":True,
    "MAIL_USERNAME": 'decaquestions@email.cz',
    "MAIL_PASSWORD": 'Bonbon01'
}

app.config.update(mail_settings)
mail = Mail(app)


@app.route('/')
def index():
    GlobalUsername = escape(session['username'])
    return render_template('index.html', usr=GlobalUsername)

@app.route('/action/newuser')
def registrace():
    return render_template('registrace.html')

@app.route('/back/newuser', methods=["POST"])
def newuser():
        jmeno = request.form['first_name']
        prijmeni = request.form['last_name']
        email = request.form['email']
        heslo = request.form['password']
        nickname = request.form['nickname']
        verifyEmail = verify.verify_mail(email)
        if verifyEmail == "ok":
            con = sql.connect('main.db')
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute('INSERT INTO uzivatele (uzivatel, heslo, email, jmeno, prijmeni)  VALUES (?, ?, ?, ?, ?);', [nickname, heslo, email, jmeno, prijmeni])
            con.commit()
            con.close()
            return redirect('/back/logout')
        else:
            return("Zadaný email nepochází z domény @decathlon.com")

@app.route('/newquestion')
def newquestion():
    GlobalUsername = escape(session['username'])
    return render_template('dotaz.html', usr=GlobalUsername)

@app.route('/prehled')
def prehled():
    GlobalUsername = escape(session['username'])
    con = sql.connect('main.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('SELECT *, ROWID FROM dotazy ORDER BY vlozeno DESC, vcase DESC;')
    rows = cur.fetchall()
    return render_template('vypis.html', rows=rows, usr=GlobalUsername)

@app.route('/prehled:<kategorie>')
def prehledby(kategorie):
    GlobalUsername = escape(session['username'])
    con = sql.connect('main.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('SELECT *, ROWID FROM dotazy WHERE kategorie = ?;', [kategorie])
    rows = cur.fetchall()
    return render_template('vypis.html', rows=rows, usr=GlobalUsername)



@app.route('/back/newquestion', methods=["POST"])
def savequestion():
        name = escape(session['username'])
        con = sql.connect('main.db')
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
        kategorie = request.form['kategorie']
        dotaz = request.form['dotaz']
        anonym = request.form['anonymita']
        if anonym == "jsemsrab":
            jj = "Anonymní"
            pp = "příspěvek"
            cur.execute('INSERT INTO dotazy (email, kategorie, dotaz, jmeno, prijmeni)  VALUES (?, ?, ?, ?, ?);', [email, kategorie, dotaz, jj, pp])
            con.commit()
            con.close()
            con = sql.connect('main.db')
            cur = con.cursor()
            cur.execute('SELECT ROWID FROM dotazy WHERE email = ? AND dotaz = ?;', [email, dotaz])
            rowid = cur.fetchone()
        #    return redirect('/mailing/newquestion/rowid')
            return redirect('/')
        else:
            cur.execute('INSERT INTO dotazy (email, kategorie, dotaz, jmeno, prijmeni)  VALUES (?, ?, ?, ?, ?);', [email, kategorie, dotaz, j, p])
            con.commit()
            con.close()
            con = sql.connect('main.db')
            cur = con.cursor()
            cur.execute('SELECT ROWID FROM dotazy WHERE email = ? AND dotaz = ?;', [email, dotaz])
            rowid = cur.fetchone()
        #    return redirect('/mailing/newquestion/rowid')
            return redirect('/')
@app.route('/mailing/newquestion/<rowid>')
def mailnq(rowid):
    rowid = rowid
    con = sql.connect('main.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('SELECT kategorie, dotaz FROM dotazy WHERE rowid = ?', [rowid])
    rows = cur.fetchall()

    for row in rows:
        dotaz[row] = rows['dotaz']

    msg = Message(subject="Nový dotaz od spoluhráče",
                  sender="Decathlon | Questions",
                  recipients="kgilich@gmail.com")

    msg = "Dobrý den, právě byla položena nová otázka."
    mail.send(msg)

    return redirect('/')
# overovani uzivatele
@app.route('/back/auth', methods=['POST'])
def auth():
    name = request.form['jmeno']
    heslo = request.form['heslo']
    vysledek = overeni(name, heslo)
    if vysledek is not "neni":
        session['username'] = request.form['jmeno']
        session['logged in'] = True
        return redirect("/")
    else:
        return("Špatné heslo/jméno")
    
@app.route('/komentare:<postid>', methods=['GET'])
def vypiskomentaru(postid):
    GlobalUsername = escape(session['username'])
    con = sql.connect('main.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('SELECT * FROM komentare WHERE postID = ?;', [postid])
    rows = cur.fetchall()

    return render_template('komentare.html', rows=rows, row=postid, usr=GlobalUsername)

@app.route('/back/comment:<postid>', methods=['POST'])
def poslikometar(postid):
        postID = postid
        komentar = request.form['komentar']
        name = escape(session['username'])
        con = sql.connect('main.db')
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
        con = sql.connect('main.db')
        cur = con.cursor()
        cur.execute('INSERT INTO komentare (postID, komentar, email, jmeno, prijmeni)  VALUES (?, ?, ?, ?, ?);', [postID, komentar, email, j, p])
        con.commit()
        con.close()
        return redirect('/prehled')

def overeni(name, heslo):
    con = sql.connect('main.db')
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute('SELECT ROWID FROM uzivatele WHERE uzivatel=? AND heslo=?', [name, heslo])
    if cur.fetchall():
        return("je")
    else:
        return("neni")
# konec overovani

def NajdiJmeno(email):
    con = sql.connect('main.db')
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