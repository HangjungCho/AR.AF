from sqlalchemy import create_engine
from flask import Flask, url_for, render_template, request, redirect, session, jsonify, make_response, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import time
from sqlalchemy.sql.expression import desc
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///screen.db'
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = "user"
    
    id = db.Column(db.String, primary_key = True)
    password = db.Column(db.String)

    def __init__(self, id, password):
        self.id = id
        self.password = password
        
    def __repr__(self):
        return "<User('%s', '%s')>" % (self.id,self.password)
        
        
class Product(db.Model):
    __tablename__ = "product"
    
    product = db.Column(db.String, primary_key = True)
    date = db.Column(db.Integer)
    error = db.Column(db.String)
    picture = db.Column(db.String)
    
    def __init__(self, product, date, error, picture):
        self.product = product
        self.date = date
        self.error = error
        self.picture = picture
        
    def __repr__(self):
        return "<Product('%s', '%s', '%s','%s')>" % (self.product,self.date,self.error, self.picture)

    
def format_datetime(timestamp):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H-%M')



@app.route("/")
def main():
    return render_template("main.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        id = request.form["id"]
        password = request.form["password"]
        try:
            user_data = user.query.filter_by(id = id, password = password).first()
            if user_data is not None :
                session ["user_id"] = user_data.id
                session ["logged_in"] = True
                return redirect(url_for("main"))
            else :
                message = "you're not a member"
                return render_template("message.html", msg = message)
        except:
            message = "exception!!"
            return render_template("message.html", msg = message)    
   

             
    
app.jinja_env.filters['datetimeformat'] = format_datetime

if __name__ == "__main__":
    app.debug = True
#    db.create_all()
    # app.secret_key = "1234567890"
    app.run()
        
    
        