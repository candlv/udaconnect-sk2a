import sqlite3
import logging, sys

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort, HTTPException



# Define the Flask application
app = Flask(__name__)

app.config['SECRET_KEY'] = 'your secret key'
app.config['COUNTER'] = 0
counter = app.config['COUNTER']


# create logger app
logger = logging.getLogger('app')

# Basic configration values
logging.basicConfig( level=logging.DEBUG)
formatter = logging.Formatter('%(levelname)s:%(name)s:%(asctime)s, %(message)s')

# create stdout logger 
stdout = logging.StreamHandler(sys.stdout)
stdout.setFormatter(formatter)
logger.addHandler(stdout)

# create stderr logger 
stderr = logging.StreamHandler(sys.stderr)
stderr.setLevel(logging.ERROR)
stderr.setFormatter(formatter)
logger.addHandler(stderr)


def get_db_connection():
    """This function connects to database with the name `database.db`"""
    global counter
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    counter += 1
    return connection


# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    connection.close()
    return post

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    logger.info('Home page is retrieved')
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if not post:
        logger.error('Article not found')
        return render_template('404.html'), 404
    else:
        logger.info('Article {} is retrieved'.format(post['title']))
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logger.info('About Us page is retrieved')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            logger.info('Article {} is created successfully'.format(title))
            return redirect(url_for('index'))
    return render_template('create.html')


@app.errorhandler(500)
def internal_error(e):
    return jsonify(result="ERROR - unhealthy"), 500


@app.route('/healthz')
def helath():
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?', (1,)).fetchone()
    connection.close()
    
    if not post:
      abort(500)
      
    return jsonify(result="OK - healthy"), 200


@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    count = connection.execute('SELECT * from posts').fetchall()
    connection.commit()
    connection.close()
    return {"status":"success","code":0,"data":{"post_count": len(count),"db_connection_count": counter}}


   

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
