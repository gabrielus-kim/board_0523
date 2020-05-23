from flask import Flask, request, session
from flask import render_template, abort, redirect
import pymysql
from datetime import datetime

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

def get_menu():
    if am_i_here() == False:
        return f"""현재 시각은 : {datetime.now()}"""
    else:
        cur=db.cursor()
        cur.execute(f"""
            select id, title from topic
        """)
        menu_dic=cur.fetchall()
        menu=[]
        for i in menu_dic:
            menu.append(f"""<li><a href='/{i['id']}'>{i['title']}</a></li>""")
        return '\n'.join(menu)

@app.route('/')
def index():
    if am_i_here() == True:
        title = "안녕하세요?"
    else:
        title = "Login 해주세요."
    return render_template('index.html',
                            owner=who_am_i(),
                            menu=get_menu(),
                            title=title)

@app.route('/<id>')
def get_post(id):
    cur=db.cursor()
    cur.execute(f"""
        select id, title, description from topic 
        where id='{id}'
    """)
    content=cur.fetchone()

    return render_template('index.html',
                            owner=who_am_i(),
                            menu=get_menu(),
                            id=content['id'],
                            title=content['title'],
                            message=content['description'])

@app.route('/write', methods=['GET','POST'])
def post_write():
    if am_i_here() == False:
        title = "Login 후 사용할 수 있읍니다."
        return render_template('index.html',
                            owner=who_am_i(),
                            menu=get_menu(),
                            title=title)
    else:
        title='게시판 내용을 입력해 주세요.'
        if request.method =='POST':
            cur=db.cursor()
            cur.execute(f"""
                insert into topic (title, description, created, author_id)
                values ('{request.form['title']}',
                        '{request.form['content']}',
                        '{datetime.now()}',
                        '{session['user']['id']}')
            """)
            db.commit()
            return redirect('/') 
    return render_template('write.html',
                            owner=who_am_i(),
                            title=title)

@app.route('/delete/')
def delete_error():
    if am_i_here() == True:
        title='Menu 선택후 삭제할 수 있읍니다.'
    else:
        title='Login 후 사용할 수 있읍니다.'
    return render_template('index.html',
                            owner=who_am_i(),
                            menu=get_menu(),
                            title=title)

@app.route('/update/')
def update_error():
    if am_i_here() == True:
        title='Menu 선택후 수정할 수 있읍니다.'
    else:
        title='Login 후 사용할 수 있읍니다.'
    return render_template('index.html',
                            owner=who_am_i(),
                            menu=get_menu(),
                            title=title)

@app.route('/delete/<id>')
def post_delete(id):
    cur=db.cursor()
    cur.execute(f"""
        delete from topic where id='{id}'
    """)
    db.commit()
    return redirect('/')

@app.route('/update/<id>', methods=['GET','POST'])
def post_update(id):
    cur=db.cursor()
    cur.execute(f"""
        select id, title, description from topic
        where id='{id}'
    """)
    content=cur.fetchone()
    if request.method =='POST':
        cur=db.cursor()
        cur.execute(f"""
            update topic set title='{request.form['title']}',
                            description='{request.form['content']}',
                            created='{datetime.now()}',
                            author_id='{session['user']['id']}'
            where id='{id}'
        """)
        db.commit()
        return redirect('/') 
    return render_template('update.html',
                            owner=who_am_i(),
                            id=content['id'],
                            title=content['title'],
                            message=content['description'])


@app.route('/login', methods=['GET','POST'])
def login():
    if am_i_here() == True:
        title = "Login 상태 입니다."
        return render_template('index.html',
                            owner=who_am_i(),
                            menu=get_menu(),
                            title=title)
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

@app.route('/join', methods=['GET','POST'])
def join():
    if am_i_here() == True:
        title = session['user']['name']+" 님은 이미 회원가입 상태 입니다."
        return render_template('index.html',
                            owner=who_am_i(),
                            menu=get_menu(),
                            title=title)
    else:
        title = "가입 등록후 사용해 주세요"
        if request.method == 'POST':
            cur = db.cursor()
            cur.execute(f"""
                select name from author where name='{request.form['id']}'
            """)
            user=cur.fetchone()
            if user is None:
                cur=db.cursor()
                cur.execute(f"""
                    insert into author (name, profile, password)
                    values ('{request.form['id']}',
                            '{request.form['pf']}',
                            SHA2('{request.form['pw']}',256))
                """)
                db.commit()
                title=request.form['id']+"님, 가입해주셔서 감사합니다. Login 후 사용해 주세요."
                return render_template('index.html',
                                        owner=who_am_i(),
                                        menu=get_menu(),
                                        title=title)
            else:
                title=request.form['id']+"은 이미 등록된 LogIn ID 입니다."        
    return render_template('join.html',
                            owner=who_am_i(),
                            title=title)

@app.route('/withdraw')
def withdraw():
    if am_i_here() == True:
        cur=db.cursor()
        cur.execute(f"""
            delete from author where name='{session['user']['name']}'
        """)
        db.commit()
        title = session['user']['name']+"님, 정상적으로 회원 탈퇴 되었읍니다."
        session.pop('user',None)
    else:
        title = "Login 후 회원 탈퇴 부탁드립니다."
    return render_template('index.html',
                            owner=who_am_i(),
                            menu=get_menu(),
                            title=title)

@app.route('/favicon.ico')
def favicon():
    return abort(404)


app.run(port='8000')