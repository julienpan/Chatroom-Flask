#! python3

from flask import Flask, render_template, redirect, url_for, session, request
from flask_socketio import SocketIO, send
import psycopg2
from datetime import datetime
import sys
import keyword, html

sys.stdout.write("Hello from Python %s\n" % (sys.version,))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
# connection = psycopg2.connect("host='localhost' dbname='chat_db' user='postgres' password='admin'")
connection = psycopg2.connect("host='ec2-52-72-34-184.compute-1.amazonaws.com' port='5432' dbname='dcqsqk92pdhf6o' user='ugpndzjemldrwf' password='5f52b1ba3113ab3af88a8124423e664a3559fbe43b5b071acd88f430e12b8b0f'")
# "postgres://ugpndzjemldrwf:5f52b1ba3113ab3af88a8124423e664a3559fbe43b5b071acd88f430e12b8b0f@ec2-52-72-34-184.compute-1.amazonaws.com:5432/dcqsqk92pdhf6o"
mycursor = connection.cursor()
socketio = SocketIO(app)

def insert_client(user, password):
# insert client into database
 sql = "INSERT INTO clients(UserName, Password, CreateDate) VALUES ('%s', '%s', '%s');" % (user, password, datetime.now())
 try:
  mycursor.execute(sql)
  connection.commit()
 except:
  connection.rollback()

def insert_message(user, message):
 sql = "INSERT INTO messages(UserName, Messages, CreateDate) VALUES ('%s', '%s', '%s');" % (user, message, datetime.now())
 try:
  mycursor.execute(sql)
  connection.commit()
 except:
  connection.rollback()

def delete_message(id):
 sql = "DELETE FROM messages WHERE Id='%s'" % (id)
 try:
  mycursor.execute(sql)
  connection.commit()
 except:
  connection.rollback()

def update_message(message, id):
 sql = "UPDATE messages SET Messages='%s' WHERE Id='%s'" % (message, id)
 try:
  mycursor.execute(sql)
  connection.commit()
 except:
  connection.rollback()

def get_client2(user):
 sql2 = "SELECT UserName, Password FROM clients c WHERE c.UserName='%s'" % (user)
 mycursor.execute(sql2)
 return mycursor.fetchall()

def get_message():
 sql = "SELECT Id, UserName, Messages FROM messages ORDER BY Id DESC"
 mycursor.execute(sql)
 return mycursor.fetchall()

@app.route('/')
def index():
 return redirect(url_for('login'))

@app.route('/connexion', methods=["POST", "GET"])
def login():
 if "user" in session:
  return redirect('/chat')
 if request.method == "POST":
  username=request.form["username"]
  password=request.form["password"]
  client=get_client2(username)
  cl=client[0]
  if cl[1] == password or "user" in session:
   session['user'] = username
   return redirect('/chat')
  else:
   return """<script>alert("Identifiant ou Mdp incorrect."); location.replace('/connexion');</script>"""
 return render_template('login.html', clients=get_client2("user"))

@app.route('/inscription', methods=["POST", "GET"])
def register():
 if "user" in session:
  return redirect('/chat')
 if request.method == "POST":
  username=request.form["username"]
  password=request.form["password"]
  password2=request.form["password2"]
  if password == password2:
   insert_client(username, password)
   return redirect('/connexion')
  else:
   return """<script>alert("Les mots de passe ne sont pas pareils."); location.replace('/inscription'); </script>"""
 return render_template('register.html')

@socketio.on('message')
def handleMessage(usr, msg): 
 insert_message(session["user"], msg)
 msg = str(session["user"]+": "+msg)
 print(msg)
 send(msg, broadcast=True)

@socketio.on('message2')
def handleMessage(usr, msg): 
 update_message(session["user"], msg)
 msg = str(session["user"]+": "+msg)
 print(msg)
 send(msg, broadcast=True)

@app.route('/chat', methods=["POST", "GET"])
def chat():
 if "user" in session:
  print("Utilisateur")
 if request.method == "POST":
  print("Utilisateur2")

  if request.form["valider32"] == "Supprimer":
   repere=request.form["repere233"]
   delete_message(repere)
   return redirect('/chat')

  if request.form["valider32"] == "Modifier":
   messages=request.form["messages2"]
   repere=request.form["repere2"]
   update_message(messages, repere)
   return redirect('/chat')

 return render_template('index.html', user=session["user"], messages=get_message(), clients2=get_client2("user"))

@app.route('/logout')
def logout():
 session.pop("user")
 return redirect('/connexion')

if __name__ == '__main__':
 socketio.run(app, debug=True)


