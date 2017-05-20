import sqlite3
from flask import Flask,render_template

app = Flask(__name__)
app.debug = True


@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/feedback/')
def feedback():
    conn = sqlite3.connect(r'.\db\feedback.db')
    c = conn.cursor()
    sql = 'select ROWID,CategoryName from category'
    categories = c.execute(sql).fetchall()
    return render_template('post.html',categories=categories)

@app.route('/login/')
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run()