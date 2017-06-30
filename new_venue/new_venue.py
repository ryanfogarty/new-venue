import string
import random
import sqlite3
import os
import io
import base64
from base64 import b64encode, b64decode
import codecs
import PIL
from PIL import Image
from werkzeug import secure_filename
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, send_file

app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , code_gen.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'venues.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default',
))
app.config.from_envvar('VENUE_SETTINGS', silent=True)

def connect_db():
    #Connects to the specific database.
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    #Opens a new database connection if there is none yet for the
    #current application context.
    
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    #Closes the database again at the end of the request.
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
        
def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    
@app.cli.command('initdb')
def initdb_command():
    #Initializes the database.
    init_db()
    print('Initialized the database.')
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            #flash('You were logged in')
            return redirect(url_for('mainpage'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))
 
 
@app.route('/', methods = ['GET','POST'])
def mainpage():
   if session.get('logged_in'):   
      return render_template('new_venue.html')
   else:
      return render_template('login.html')

@app.route('/new_venue', methods = ['GET','POST'])
def new_venue():
   #if request.method == 'POST':
       name = request.form['venue_name'] 
       venue_address = request.form['venue_address']
       venue_password = request.form['venue_password']   
       pic = request.files['venue_picture']    
       
       conn = get_db()
       c = conn.cursor()
       c.execute("SELECT venue_name FROM venues") 
       all_venues = c.fetchall()
       for a_venue in all_venues:
          if a_venue[0] == name:
             return render_template('new_venue.html')
       



       thumb = Image.open(pic)
       thumb = thumb.resize((500,300),PIL.Image.ANTIALIAS)
       in_mem_file = io.BytesIO()
       thumb.save(in_mem_file,format="jpeg")
       in_mem_file.seek(0)
       img_bytes = in_mem_file.read()
       base64_encoded_result_bytes = base64.b64encode(img_bytes)
       encode = base64_encoded_result_bytes.decode('ascii')    
       
       
  
      

       c.execute("INSERT into venues(venue_name,venue_address,venue_password,venue_picture)VALUES(?,?,?,?)",(name,venue_address,venue_password,encode))
       conn.commit()
       c.execute("SELECT venue_picture from venues")
       pic2 = c.fetchall()
       picture_list = []
       for i in pic2:
              render_picture = i[0]
              picture_list.append(render_picture)    #list of all pictures, resized to fit page
       c.execute("SELECT venue_name from venues")
       all_venues = c.fetchall()

      
       c.close()

       return render_template('success.html',picture_list=zip((reversed(picture_list)),(reversed(all_venues))))
    
  

