from flask import Flask, request, session
from flask import render_template, abort, redirect
import pymysql

app=Flask(__name__,
        template_folder='template')

db=pymysql.connect(user='root',
                passwd='avante',
                host='localhost',
                db='web',
                charset='utf8',
                cursorclass=pymysql.cursors.DictCursor)

app.config['ENV'] = 'Development'
app.config['DEBUG'] = True
app.secret_key='who are you?'

def who_am_i():
    # if 'user' in session:
    #     owner=session['user']['name']
    # else:
    #     owner = "Hi! Every one"
    # return owner
    return session['user']['name'] if 'user' in session else "Hi! Every one"

def am_i_here():
    return True if 'user' in session else False

@app.route('/')
def index():
    if am_i_here() == True:
        title = "안녕하세요?"
    else:
        title = "Login 해주세요."
    return render_template('index.html',
                            owner=who_am_i(),
                            title=title)

@app.route('/login', methods=['GET','POST'])
def login():
    if am_i_here() == True:
        return redirect('/')
    else:
        title = "Login 해주세요."

    if request.method == 'POST':
        cur=db.cursor()
        cur.execute(f"""
            select id, name from author where name='{request.form['id']}'
        """)
        user=cur.fetchone()
        if user is None:
            title='Login Id을 확인해 주세요'
        else:
            cur=db.cursor()
            cur.execute(f"""
                select id, name, password from author
                where name = '{request.form['id']}' and
                password = SHA2('{request.form['pw']}',256)
            """)
            user=cur.fetchone()
            if user is None:
                title='PassWord 를 확인해 주세요'
            else:
                session['user'] =user
                return redirect('/')
    return render_template('login.html',
                            owner=who_am_i(),
                            title=title)

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

@app.route('/favicon.ico')
def favicon():
    return abort(404)


app.run(port='8000')