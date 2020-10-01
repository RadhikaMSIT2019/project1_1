import os
import sys
from datetime import datetime

from flask import Flask, render_template, request,redirect,url_for, flash, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import *  # create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import *  # scoped_session, sessionmaker

from werkzeug.debug import DebuggedApplication
# def load_config(mode):
#     """Load config."""
#     try:
#         if mode == 'PRODUCTION':
#             from .production import ProductionConfig
#             return ProductionConfig
#         elif mode == 'TESTING':
#             from .testing import TestingConfig
#             return TestingConfig
#         else:
#             from .development import DevelopmentConfig
#             return DevelopmentConfig
#     except ImportError:
#         from .default import Config
#         return Config

# config = load_config(mode=os.environ.get('FLASK_ENV'))
app = Flask(__name__)
# app.debug = True
# app.config.from_object(os.environ.get('FLASK_ENV'))
# if app.debug:
#     app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['development'] = True
app.config['SECRET_KEY'] = '#RR#'
Session(app)
user = ""

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
# engine = create_engine("postgres://uvzriayrtbengf:003c06b304340ce57dd5f14d97b848b8dcf07ba3c68e7ce9f9144e748dab07de@ec2-54-152-40-168.compute-1.amazonaws.com:5432/d5oa914l0lfkcv")
db = scoped_session(sessionmaker(bind=engine))
print(engine.table_names(),file=sys.stdout)
# db=SQLAlchemy(app)

Base = declarative_base()
class Users(Base):
    __tablename__ = "USERS"
    email = Column(String, primary_key=True, nullable=False)
    fname = Column(String)
    lname = Column(String)
    pwrd = Column(String)
    date = Column(DateTime)

class  Books(Base):
    __tablename__ = "BOOKS"
    isbn = Column(String, primary_key=True, nullable=False)
    title = Column(String)
    author = Column(String)
    year = Column(Integer)

@app.route("/")
def index2():
    return "Project 1: TODO"


@app.route("/home")
def userHome():
    if 'email' in session:
        return render_template('index.html', email=session['email'])
    return render_template('base.html', email=None)



@app.route("/base")
def base():
    return render_template('base.html')

@app.route("/index")
def index():
    if 'email' in session:
        return render_template('index.html',email=session['email'])
    return render_template('base.html', email=None)



@app.route("/register")
def register():
    if not engine.dialect.has_table(engine,"USERS"):  # If table don't exist, Create.
        # db_engine = connect_db()
        # path='./static/css/style.css'
        Users.__table__.create(bind=engine, checkfirst=True)
    if "email" in session:
        print("session present while registrering")
        return render_template('register.html', email=session['email'])
    return render_template('register.html', email=None)

@app.route("/registration",methods=["POST"])
def registration():
    rfname=request.form.get("first_name")
    rlname=request.form.get("last_name")
    remail=request.form.get("email")
    rpassword=request.form.get("password")
    rcpassword=request.form.get("confirm_password")

    if "login" in request.form:
        try:
            print('in login')
            db = scoped_session(sessionmaker(bind=engine))
            query = db.query(Users).filter(Users.email == remail)
            name = query.first()
            # print(name.email)
            if name is not None and name.email == remail and name.pwrd == rpassword:
                print('session created')
                session['email'] = name.email
                user = name.email
                # s = session['email']
                return render_template('search.html', email=user)
            elif name is not None and name.email == remail and name.pwrd != rpassword:
                print('Incorrect password, try again')
                # session['email'] = name.email
                flash('Incorrect password, try again')
                # s = session['email']
                return render_template('register.html', email=None)
            else:
                print('User not registered,register before you login')
                flash('User not registered,register before you login')
                # return redirect(url_for('register'))
                return render_template('register.html',email=None)
        except SQLAlchemyError as e:
            print(e)
            return render_template('fail.html',path='./static/css/style.css')
        finally:
            db.close()
    else:
        print("in register method")
        if rpassword == rcpassword:
            # data = {'a': 5566, 'b': 9527, 'c': 183}
            try:
                db = scoped_session(sessionmaker(bind=engine))
                query = db.query(Users).filter(Users.email == remail)
                print(remail)
                if query.first() != None:
                    print('User already exists')
                    flash('User already exists')
                    return render_template('register.html', email=None)
                else:
                    print('Inserting user')
                    now = datetime.now()
                    db = scoped_session(sessionmaker(bind=engine))
                    row = Users(email=remail,fname=rfname,lname=rlname,pwrd=rpassword,date=now)
                    db.add(row)
                    db.commit()
                    return render_template('index.html', email=None)

            except SQLAlchemyError as e:
                print(e)
                return render_template('fail.html',path='./static/css/style.css')
            finally:
                db.close()
                # return render_template('success.html',path='./static/css/styles.min.css')
        else:
            print("confirmation does not match")
            flash('confirmation password does not match with the Entered password, Try again')
            return render_template('register.html', email=None)
            # return redirect(url_for('register'))

    #     print(remail+" , "+rfname+" , "+rlname,file=sys.stdout)
    #     print(remail+" , "+rfname+" , "+rlname, file=sys.stderr)
    #
    # return remail+" , "+rfname+" , "+rlname
@app.route("/search",methods=["POST"])
def search():
    isbn=request.form.get("isbn")
    title=request.form.get("title")
    author=request.form.get("author")
    # print("isbn = "+isbn,", title = "+title,", author = "+author)

    if isbn!="" and title=="" and author=="":
        try:
            db = scoped_session(sessionmaker(bind=engine))
            query = db.query(Books).filter(Books.isbn == isbn)
            if query != None:
                # r = query.all()
                # print(r)
                # for book in r:
                #     print(f"added{book.title} with number {book.isbn} written by {book.author} published in the year {book.year}")
                return render_template('books.html',row = query.all(),email=session['email'])
            else :
                flash("there are no books available with the specified details,try with more specific details")
                return render_template('search.html',email=session['email'])
        except SQLAlchemyError as e:
            print(e)
            return render_template('fail.html',path='./static/css/style.css')
        finally:
            db.close()
    elif isbn=="" and title!="" and author=="":
        try:
            db = scoped_session(sessionmaker(bind=engine))
            query = db.query(Books).filter(Books.title == title)
            if query != None:
                # r = query.all()
                # print(r)
                # for book in r:
                #     print(f"added{book.title} with number {book.isbn} written by {book.author} published in the year {book.year}")
                return render_template('books.html',row = query.all(),email=session['email'])
            else :
                flash("there are no books available with the specified details,try with more specific details")
                return render_template('search.html',email=session['email'])
        except SQLAlchemyError as e:
            print(e)
            return render_template('fail.html',path='./static/css/style.css')
        finally:
            db.close()
    elif isbn=="" and title=="" and author!="":
        try:
            db = scoped_session(sessionmaker(bind=engine))
            query = db.query(Books).filter(Books.author == author)
            if query != None:
                # r = query.all()
                # print(r)
                # for book in r:
                #     print(f"added{book.title} with number {book.isbn} written by {book.author} published in the year {book.year}")
                return render_template('books.html',row = query.all(),email=session['email'])
            else :
                flash("there are no books available with the specified details,try with more specific details")
                return render_template('search.html',email=session['email'])
        except SQLAlchemyError as e:
            print(e)
            return render_template('fail.html',path='./static/css/style.css')
        finally:
            db.close()
    elif isbn!="" and title!="" and author=="":
        try:
            db = scoped_session(sessionmaker(bind=engine))
            query = db.query(Books).filter(Books.title == title,Books.isbn == isbn)
            if query != None:
                # r = query.all()
                # print(r)
                # for book in r:
                #     print(f"added{book.title} with number {book.isbn} written by {book.author} published in the year {book.year}")
                return render_template('books.html',row = query.all(),email=session['email'])
            else :
                flash("there are no books available with the specified details,try with more specific details")
                return render_template('search.html',email=session['email'])
        except SQLAlchemyError as e:
            print(e)
            return render_template('fail.html',path='./static/css/style.css')
        finally:
            db.close()
    elif isbn!="" and title=="" and author!="":
        try:
            db = scoped_session(sessionmaker(bind=engine))
            query = db.query(Books).filter(Books.author == author,Books.isbn == isbn)
            if query != None:
                # r = query.all()
                # print(r)
                # for book in r:
                #     print(f"added{book.title} with number {book.isbn} written by {book.author} published in the year {book.year}")
                return render_template('books.html',row = query.all(),email=session['email'])
            else :
                flash("there are no books available with the specified details,try with more specific details")
                return render_template('search.html',email=session['email'])
        except SQLAlchemyError as e:
            print(e)
            return render_template('fail.html',path='./static/css/style.css')
        finally:
            db.close()
    elif isbn=="" and title!="" and author!="":
        try:
            db = scoped_session(sessionmaker(bind=engine))
            query = db.query(Books).filter(Books.title == title,Books.author == author)
            if query != None:
                # r = query.all()
                # print(r)
                # for book in r:
                #     print(f"added{book.title} with number {book.isbn} written by {book.author} published in the year {book.year}")
                return render_template('books.html',row = query.all(),email=session['email'])
            else :
                flash("there are no books available with the specified details,try with more specific details")
                return render_template('search.html',email=session['email'])
        except SQLAlchemyError as e:
            print(e)
            return render_template('fail.html',path='./static/css/styles.css')
        finally:
            db.close()
    else:
        try:
            db = scoped_session(sessionmaker(bind=engine))
            query = db.query(Books).filter(Books.title == title,Books.author == author,Books.isbn == isbn)
            if query != None:
                # r = query.all()
                # print(r)
                # for book in r:
                #     print(f"added{book.title} with number {book.isbn} written by {book.author} published in the year {book.year}")
                return render_template('books.html',row = query.all(),email=session['email'])
            else :
                flash("there are no books available with the specified details,try with more specific details")
                return render_template('search.html',email=session['email'])
        except SQLAlchemyError as e:
            print(e)
            return render_template('fail.html',path='./static/css/style.css')
        finally:
            db.close()

@app.route("/booksearch/<string:isbn>")
def booksearch():
    pass

@app.route("/searchtest")
def searchtest():
    return render_template('search.html',email=None)



@app.route("/login",methods=["POST"])
def login():
    return render_template('main.html',path='./static/css/style.css')

@app.route("/login_form")
def login_form():
    session.pop('email', None)
    return render_template('index.html',path='./static/css/style.css', email=None)

@app.route("/main")
def data():
    try:
        db = scoped_session(sessionmaker(bind=engine))
        query = db.query(Users).order_by(Users.date)
        return render_template('login.html',row = query.all())
    except SQLAlchemyError as e:
        print(e)
        return render_template('fail.html',path='./static/css/style.css')
    finally:
        db.close()


if __name__ == "__main__":
    # app.secret_key = "#KR#"
    app.run(debug=True)
    # Session(app)
