import sqlite3
from flask import Flask,render_template,request,redirect,url_for
from flask import g,flash,send_from_directory,session,make_response
from datetime import datetime,timedelta
import os
from account.views import RegUser,UserLogin,MyRegUser
from article.views import article
from product.views import product


app = Flask(__name__)
app.debug = True
app.secret_key = "SDAGERT#$%^WSG&$%YD343"


DATABASE_URL = r'.\db\feedback.db'
UPLOAD_FOLDER = r'.\uploads'
ALLOWED_EXTENSIONS = ['.jpg','.png','gif']


app.register_blueprint(article,url_prefix='/news/')
app.register_blueprint(product,url_prefix='/products/')

#检查文件是否允许上传
def allowed_file(filename):
    # filename = 'wlirlwjfljfl.JPG'
    _,ext = os.path.splitext(filename)
    return ext.lower() in ALLOWED_EXTENSIONS



# 将游标获取的tuple根据数据库列表转换为dict
def make_dicts(cursor,row):
    return dict((cursor.description[i][0],value)for i,value in enumerate(row))

# 获取(建立数据库连接)
def get_db():
    db = getattr(g,'_database',None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE_URL)
        db.row_factory = make_dicts
    return db


# 执行SQL语句不返回数据结果
def execute_sql(sql,prms=()):
    c = get_db().cursor()
    c.execute(sql,prms)
    c.connection.commit()


# 执行用于选择数据的SQL语句
def query_sql(sql,prms=(),one=False):
    c = get_db().cursor()
    result = c.execute(sql,prms).fetchall()
    c.close()
    return (result[0] if result else None) if one else result


# 关闭连接（在当前APP上下文销毁时关闭连接）
@app.teardown_appcontext
def close_connection(exeption):
    db = getattr(g,'_database',None)
    if db is not None:
        db.close()



@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/feedback/')
def feedback():
    conn = sqlite3.connect(DATABASE_URL)
    c = conn.cursor()

    sql = 'select ROWID,CategoryName from category'
    categories = c.execute(sql).fetchall()
    c.close()
    conn.close()
    return render_template('post.html',categories = categories)

@app.route('/login/',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        pwd = request.form.get('pwd')
        sql = 'select count(*) as [Count] from UserInfo WHERE UserName=? AND Password=?'
        result = query_sql(sql,(username,pwd),one=True)
        if int(result.get('Count')) > 0:
            session['admin'] = username
            return redirect(url_for('feedback_list'))
        flash('您输入的用户名或密码不正确！')
    return render_template('login.html')

@app.route('/logout/')
def logout():
    session.pop('admin')
    return redirect(url_for('feedback_list'))


@app.route('/post_feedback/',methods=['POST'])
def post_feedback():
    #如果当前请求方法为post
    if request.method == 'POST':
        #获取表单值
        book_number = request.form['book_number']
        title = request.form.get('title')
        kind_number = request.form.get('kind_number',1)
        author = request.form.get('author')
        press = request.form.get('press')
        ISBN = request.form.get('ISBN')
        img_path = None

        #if request.file.get(screenshot',None):
        if 'screenshot' in request.files:
            # 获取图片上传，并且获取文件名，以便和其他字段一并插入数据库
            img = request.files['screenshot']
            if allowed_file(img.filename):
                img_path = datetime.now().strftime('%Y%m%d%H%M%f')+ os.path.splitext(img.filename)[1]
                img.save(os.path.join(UPLOAD_FOLDER,img_path))

        text = request.form.get('text')
        sales_status = request.form.get('sales_status')
        choiceness = request.form.get('choiceness')
        Publication_date = request.form.get('Publication_date')
        Release_time = request.form.get('Release_time')

        conn = sqlite3.connect(DATABASE_URL)
        c = conn.cursor()
        sql = "insert into feedback (Book_Number, Title, Kind_Number, Author, Press, Isbn, Images, Text, Sales_Status, Choiceness, Publication_Date, Release_Time) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"
        c.execute(sql,(book_number,title,kind_number,author,press,ISBN,img_path,text,sales_status,choiceness,Publication_date,Release_time))
        conn.commit()
        conn.close()
        return redirect(url_for('feedback'))

# 呈现特定目录下的资源
@app.route('/profile/<filename>/')
def render_file(filename):
    return send_from_directory(UPLOAD_FOLDER,filename)

@app.route('/admin/save_edit/',methods=['POST'])
def save_feedback():
    if request.method == 'POST':
        rowid = request.form.get('rowid',None)
        book_number = request.form['book_number']
        title = request.form.get('title')
        kind_number = request.form.get('kind_number', 1)
        author = request.form.get('author')
        press = request.form.get('press')
        ISBN = request.form.get('ISBN')
        images = request.form.get('images')
        text = request.form.get('text')
        sales_status = request.form.get('sales_status')
        choiceness = request.form.get('choiceness')
        Publication_date = request.form.get('Publication_date')
        Release_time = request.form.get('Release_time')

        sql =  """update feedback set Book_Number = ?,Title = ?,Kind_Number = ?,Author = ?,Press = ?,Isbn = ?,Images = ?,Text = ?,Sales_Status = ?,Choiceness = ?,Publication_Date = ?,Release_Time = ? WHERE rowid = ?"""

        conn = sqlite3.connect(DATABASE_URL)
        c = conn.cursor()
        c.execute(sql,(book_number,title,kind_number,author,press,ISBN,images,text,sales_status,choiceness,Publication_date,Release_time,rowid))
        conn.commit()
        conn.close()

        return redirect(url_for('feedback_list'))

@app.route('/admin/list/')
def feedback_list():
    if session.get('admin',None) is None:
        return redirect(url_for('login'))
    else:
    #conn = sqlite3.connect(DATABASE_URL)
    #c = conn.cursor()
    #sql = 'select f.ROWID,f.*,c.CategoryName from feedback f INNER JOIN category c on c.ROWID = f.Kind_Number ORDER BY f.ROWID DESC '
    #feedbacks = c.execute(sql).fetchall()
    #conn.close()
        key = request.args.get('key','')
        sql = 'select f.ROWID,f.*,c.CategoryName from feedback f INNER JOIN category c on c.ROWID = f.Kind_Number WHERE f.Title like ? ORDER BY f.ROWID DESC '
        feedbacks = query_sql(sql,('%{}%'.format(key),))
        return render_template('feedback-list.html',items = feedbacks,keys = key)


@app.route('/admin/edit/<id>')
def edit_feedback(id=None):
    if session.get('admin',None) is None:
        return redirect(url_for('login'))
    else:
    #conn = sqlite3.connect(DATABASE_URL)
    #c = conn.cursor()

    #sql = 'select ROWID,CategoryName from category'
    #categories = c.execute(sql).fetchall()

    ##获取并绑定当前的id到指定Form表单,以备修改
    #sql = 'select rowid,* from feedback WHERE rowid = ?'
    #current_feedback = c.execute(sql,(id,)).fetchone()

    #c.close()
    #conn.close()
    #return render_template('edit.html',categories=categories,item=current_feedback)
    ##return str(current_feedback)


        sql = 'select ROWID,CategoryName from category'
        categories = query_sql(sql)
        #获取并绑定当前的id到指定Form表单,以备修改
        sql = 'select rowid,* from feedback WHERE rowid = ?'
        current_feedback = query_sql(sql, (id,), one=True)
        return render_template('edit.html',categories=categories,item=current_feedback)


@app.route('/admin/feedback/del/<id>/')
def delete_feedback(id = 0):
    #conn = sqlite3.connect(DATABASE_URL)
    #c = conn.cursor()
    #sql = "delete from feedback WHERE ROWID = ?"
    #c.execute(sql, (id,))
    #conn .commit()
    #conn.close
    sql = "delete from feedback WHERE ROWID = ?"
    execute_sql(sql,(id,))
    return redirect(url_for('feedback_list'))


@app.route('/setck/')
def set_mycookie():
    resp = make_response('ok')
    resp.set_cookie('username','义美集团',path='/',expires=datetime.now() + timedelta(days=7))
    return resp

@app.route('/getck/')
def get_mycookie():
    ck = request.cookies.get('username',None)
    if ck:
        return ck
    return '未找到'

@app.route('/rmck/')
def remove_cookie():
    resp = make_response('删除cookie')
    resp.set_cookie('username','',expires=datetime.now()+timedelta(minutes=-1))
    return resp

# 为导入的基于类的视图添加分配URL规则
#app.add_url_rule('/reg/',view_func=RegUser.as_view('reg_user'))
app.add_url_rule('/reg/',view_func=MyRegUser.as_view('reg_user'))


if __name__ == '__main__':
    app.run()




