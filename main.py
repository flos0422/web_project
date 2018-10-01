# -*- coding:utf-8 -*-
from flask import Flask, request, g, render_template, session, url_for, redirect, send_from_directory
from datetime import datetime
from werkzeug import secure_filename
import os
import hashlib
import sqlite3

DATABASE = './db/db.db'
UPLOAD_FOLDER = './uploads/'
ALLOWED_EXTENSIONS = set(['txt', 'hwp', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'pdf', 'png', 'jpg', 'jpge', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'a/4.5dsvbty7,,543/.531'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

def add_user(ID, NICK, PW, Email, num):
    PW = hashlib.sha224(b"PW").hexdigest()
    sql = "INSERT INTO user_list (ID, NICK, PW, Email, num) VALUES('%s', '%s', '%s','%s','%s')" %(ID, NICK, PW, Email, num)
    print sql
    db = get_db()
    db.execute(sql)
    res = db.commit()
    return res

def get_user(ID, PW):
    PW = hashlib.sha224(b"PW").hexdigest()
    sql = "SELECT * FROM user_list WHERE ID='%s' and PW='%s'" %(ID, PW)
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    return res

def edit_user(ID, NICK, PW, Email, num):
    PW = hashlib.sha224(b"PW").hexdigest()
    sql = "UPDATE user_list SET NICK='%s', PW='%s', Email='%s', num='%s' WHERE ID='%s'" %(NICK, PW, Email, num, ID)
    db = get_db()
    db.execute(sql)
    res = db.commit()
    return res

def write_board(b_title, b_writer, b_main, b_time, b_ID, b_file):
    sql = "INSERT INTO board (b_title, b_writer, b_main, b_time, b_ID, b_file) VALUES('%s', '%s', '%s', '%s', '%s', '%s')" %(b_title, b_writer, b_main, b_time, b_ID, b_file)
    print sql
    db = get_db()
    db.execute(sql)
    res = db.commit()
    return res

def edit_board(idx, b_title, b_writer, b_main, b_time, b_ID, b_file):
    sql = "UPDATE board SET b_title='%s', b_writer='%s', b_main='%s', b_time='%s', b_ID='%s', b_file='%s' WHERE idx='%s'" %(b_title, b_writer, b_main, b_time, b_ID, b_file, idx)
    db = get_db()
    db.execute(sql)
    res = db.commit()
    return res

def del_board(idx):
    sql = "DELETE FROM board WHERE idx='%s'" %(idx)
    db = get_db()
    db.execute(sql)
    res = db.commit()
    return res

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[-1] in ALLOWED_EXTENSIONS

def comments(b_idx, c_writer, c_main, c_time, c_ID):
    sql = "INSERT INTO comments (b_idx, c_writer, c_main, c_time, c_ID) VALUES('%s', '%s', '%s', '%s', '%s')" %(b_idx, c_writer, c_main, c_time, c_ID)
    print sql
    db = get_db()
    db.execute(sql)
    res = db.commit()
    return res

def board_comments(b_idx):
    sql = "SELECT * FROM comments WHERE b_idx='%s'" %(b_idx)
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    return res

def find_NICK(ID):
    sql = "SELECT NICK FROM user_list WHERE ID='%s'" %(ID)
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    return res[0][0]

def edit_comments(c_main, c_time, idx):
    sql = "UPDATE comments SET c_main='%s', c_time='%s'  WHERE idx='%s'" %(c_main, c_time, idx)
    db = get_db()
    db.execute(sql)
    res = db.commit()
    return res

def del_comments(idx):
    sql = "DELETE FROM comments WHERE idx='%s'" %(idx)
    db = get_db()
    db.execute(sql)
    res = db.commit()
    return res

def find_comments(idx):
    sql = "SELECT * FROM comments WHERE idx='%s'" %(idx)
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    return res

@app.route('/')
def index():
    if 'ID' in session:
        NICK = find_NICK(session['ID'])
        return render_template('index.html', data=NICK)
    else:
        a = None
        return render_template('index.html', data=a)

@app.route('/register', methods=['GET', 'POST'])
def user_add():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        print add_user(ID=request.form['ID'], NICK=request.form['NICK'], PW=request.form['PW'], Email=request.form['Email'], num=request.form['num'])
        return redirect(url_for('index'))

@app.route('/login', methods=['GET','POST'])
def user_get():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        user_id = request.form['ID']
        user_pw = request.form['PW']
        res = get_user(user_id, user_pw)
        if len(res) != 0:
            session['ID'] = user_id
            session['PW'] = user_pw
            return redirect(url_for('index'))
        else:
            return render_template('login.html')

@app.route('/logout')
def user_out():
    session.pop('ID', None)
    return redirect(url_for('index'))

@app.route('/user_edit', methods=['GET', 'POST'])
def user_edit():
    if 'ID' in session:
        if request.method == 'GET':
            sql = "SELECT * FROM user_list WHERE ID='%s'" %(session['ID'])
            db = get_db()
            rv = db.execute(sql)
            res = rv.fetchall()
            return render_template('/user_edit.html', data=res)
        else:
            user_id = session['ID']
            user_pw = request.form['PW']
            user_nick = request.form['NICK']
            user_email = request.form['Email']
            user_num = request.form['num']
            edit_user(idx, user_id, user_nick, user_pw, user_email, user_num)
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

@app.route('/board')
def board_list():
    if 'ID' in session:
        a = session['ID']
        sql = 'SELECT * FROM board'
        db = get_db()
        rv = db.execute(sql)
        res = rv.fetchall()
        return render_template('board.html', data=res)
    else:
        return redirect(url_for('index'))

@app.route('/board_write', methods=['GET', 'POST'])
def board_write():
    if 'ID' in session:
        if request.method == 'GET':
            NICK = find_NICK(session['ID'])
            return render_template('board_write.html', data=NICK)
        else:
            b_title = request.form['b_title']
            b_writer = request.form['b_writer']
            b_main = request.form['b_main']
            b_time = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
            b_ID = session['ID']
            if 'b_file' in request.files:
                b = request.files['b_file']
                if b and allowed_file(b.filename):
                    b_file = os.path.join(app.config['UPLOAD_FOLDER'])+secure_filename(b.filename)
                    b.save(b_file)
                else:
                    return u"지원하지 않는 확장자입니다"
            else:
                b_file=''
            write_board(b_title, b_writer, b_main, b_time, b_ID, b_file)
            return redirect(url_for('board_list'))
    else:
        return redircet(url_for('index'))

@app.route('/board/<idx>', methods=['GET', 'POST'])
def board_view(idx):
    if 'ID' in session:
        sql = 'SELECT * FROM board WHERE idx="%s"' %(idx)
        db = get_db()
        rv = db.execute(sql)
        res = rv.fetchall()
        ID = session['ID']
        if request.method == 'GET':
            return render_template('board_view.html', data=res, ID=ID, com=board_comments(idx))
        else:
           b_idx = res[0][0]
           c_writer = find_NICK(session['ID'])
           c_main = request.form['c_main']
           c_time = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
           c_ID = session['ID']
           comments(b_idx, c_writer, c_main, c_time, c_ID)
           return redirect(url_for('board_view',idx = res[0][0]))
    else:
        return redirect(url_for('index'))

@app.route('/board_edit/<idx>', methods=['GET', 'POST'])
def board_edit(idx):
    sql = 'SELECT * FROM board WHERE idx="%s"' %(idx)
    db = get_db()
    rv = db.execute(sql)
    res = rv.fetchall()
    if 'ID' in session:
        if session['ID'] == res[0][5]:
            if request.method == 'GET':
                return render_template('board_edit.html', data=res)
            else:
                b_title = request.form['b_title']
                b_writer = request.form['b_writer']
                b_main = request.form['b_main']
                b_time = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
                b_ID = session['ID']
                if 'b_file' in request.files:
                    b = request.files['b_file']
                    if b and allowed_file(b.filename):
                        b_file = os.path.join(app.config['UPLOAD_FOLDER'])+secure_filename(b.filename)
                        b.save(b_file)
                    else:
                        return 'Error'
                else:
                    b_file=''
                edit_board(idx, b_title, b_writer, b_main, b_time, b_ID, b_file)
                return board_view(idx)
        else:
            return board_view(idx)
    else:
        return redirect(url_for('index'))

@app.route('/board_del/<idx>')
def board_del(idx):
    if 'ID' in session:
        sql = "SELECT * FROM board WHERE idx='%s'" %(idx)
        db = get_db()
        rv = db.execute(sql)
        res = rv.fetchall()
        if session['ID'] == res[0][5]:
            del_board(res[0][0])
            return redirect(url_for('board_list'))
        else:
            return 'Error!!'
    else:
        return redirect(url_for('index'))

@app.route('/comments_edit/<idx>', methods=['GET', 'POST'])
def comments_edit(idx):
    if 'ID' in session:
        res = find_comments(idx)
        com = board_comments(res[0][1])
        if session['ID'] == res[0][5]:
            if request.method == 'GET':
                return render_template('comments_edit.html', data=res, com=com)
            else:
                c_main = request.form['c_main']
                c_time = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
                c_ID = session['ID']
                edit_comments(c_main, c_time, res[0][0])
                return redirect(url_for('board_view', idx=res[0][1]))
    return redirect(url_for('index'))

@app.route('/comments_del/<idx>')
def comments_del(idx):
    if 'ID' in session:
        res = find_comments(idx)
        if session['ID'] == res[0][5]:
            del_comments(res[0][0])
            return redirect(url_for('board_view', idx=res[0][1]))
        else:
            return 'Error!!'
    else:
        return redirect(url_for('index'))

@app.route('/board/uploads/<b_file>')
def file_download(b_file):
    return send_from_directory(app.config['UPLOAD_FOLDER'], b_file)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=1234)
