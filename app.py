import os
import sys
import requests
import json


from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_session import Session
from datetime import datetime

from sqlalchemy import *  # create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import *  # scoped_session, sessionmaker
from werkzeug.debug import DebuggedApplication


app = Flask(__name__)



# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["DATABASE_URL"] = os.getenv("DATABASE_URL")
app.config["SESSION_TYPE"] = "filesystem"
app.config['development'] = True
app.config['SECRET_KEY'] = '#RR#'
Session(app)
user = ""

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
# engine = create_engine("postgres://uvzriayrtbengf:003c06b304340ce57dd5f14d97b848b8dcf07ba3c68e7ce9f9144e748dab07de@ec2-54-152-40-168.compute-1.amazonaws.com:5432/d5oa914l0lfkcv")
#db = scoped_session(sessionmaker(bind=engine))
print(engine.table_names(), file=sys.stdout)
# db=SQLAlchemy(app)

Base = declarative_base()


class Users(Base):
    __tablename__ = "USERS"
    email = Column(String, primary_key=True, nullable=False)
    fname = Column(String)
    lname = Column(String)
    pwrd = Column(String)
    date = Column(DateTime)


class Books(Base):
    __tablename__ = "BOOKS"
    isbn = Column(String, primary_key=True, nullable=False)
    title = Column(String)
    author = Column(String)
    year = Column(Integer)


class Admin(Base):
    __tablename__ = "ADMIN"
    email = Column(String, primary_key=True, nullable=False)
    admin = Column(Boolean)


class Reviews(Base):
    __tablename__ = 'REVIEWS'
    id = Column(Integer, primary_key=True, autoincrement=True)
    review = Column(String)
    rating = Column(String)
    fname = Column(String)
    date = Column(DateTime)
    email = Column(String, ForeignKey('USERS.email'))
    isbn = Column(String, ForeignKey('BOOKS.isbn'))


@app.route("/")
def index2():
    return redirect( url_for('home'))



@app.route("/home")
def home():
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
    else:
         return render_template('base.html', email=None)





@app.route("/register")
def register():
    # If table don't exist, Create.
    if not engine.dialect.has_table(engine, "USERS"):
        # db_engine = connect_db()
        # path='./static/css/style.css'
        Users.__table__.create(bind=engine, checkfirst=True)

    if not engine.dialect.has_table(engine, "ADMIN"):
        Admin.__table__.create(bind=engine, checkfirst=True)

    if "email" in session:
        print("session present while registrering")
        return render_template('register.html', email=session['email'])
    return render_template('register.html', email=None)


@app.route("/registration", methods=["POST"])
def registration():
    rfname = request.form.get("first_name")
    rlname = request.form.get("last_name")
    remail = request.form.get("email")
    rpassword = request.form.get("password")
    rcpassword = request.form.get("confirm_password")

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
                session['fname'] = name.fname
                user = name.email

                query = db.query(Admin).filter(Admin.email == remail)
                name = query.first()

                if name is not None:
                    return redirect(url_for('main', email=user))

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
                return render_template('register.html', email=None)
        except SQLAlchemyError as e:
            print(e)
            return render_template('fail.html', path='./static/css/style.css')
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
                    row = Users(email=remail, fname=rfname,
                                lname=rlname, pwrd=rpassword, date=now)
                    db.add(row)
                    db.commit()
                    flash('USer successfully registered into DataBase')
                    return render_template('register.html', email=None)

            except SQLAlchemyError as e:
                print(e)
                return render_template('fail.html', path='./static/css/style.css')
            finally:
                db.close()
                # return render_template('success.html',path='./static/css/styles.min.css')
        else:
            print("confirmation does not match")
            flash(
                'confirmation password does not match with the Entered password, Try again')
            return render_template('register.html', email=None)
            # return redirect(url_for('register'))

    #     print(remail+" , "+rfname+" , "+rlname,file=sys.stdout)
    #     print(remail+" , "+rfname+" , "+rlname, file=sys.stderr)
    #
    # return remail+" , "+rfname+" , "+rlname


@app.route("/search", methods=["POST"])
def search():
    isbn = request.form.get("isbn")
    title = request.form.get("title")
    author = request.form.get("author")
    # print("isbn = "+isbn,", title = "+title,", author = "+author)

    if isbn != "" and title == "" and author == "":
        try:
            db = scoped_session(sessionmaker(bind=engine))
            isbn = '%'+isbn+'%'
            session['isbn'] = isbn
            session['title'] = None
            session['author'] = None
            query = db.query(Books).filter(Books.isbn.ilike(isbn))
            if query != None:
                # r = query.all()
                # print(r)
                # for book in r:
                #     print(f"added{book.title} with number {book.isbn} written by {book.author} published in the year {book.year}")
                return render_template('books.html', row=query.all(), email=session['email'])
            else:
                flash(
                    "there are no books available with the specified details,try with more specific details")
                return render_template('search.html', email=session['email'])
        except SQLAlchemyError as e:
            print(e)
            return render_template('fail.html', path='./static/css/style.css')
        finally:
            db.close()
    elif isbn == "" and title != "" and author == "":
        try:
            db = scoped_session(sessionmaker(bind=engine))
            title = '%'+title+'%'
            session['title'] = title
            session['author'] = None
            session['isbn'] = None
            query = db.query(Books).filter(Books.title.ilike(title))
            if query != None:
                # r = query.all()
                # print(r)
                # for book in r:
                #     print(f"added{book.title} with number {book.isbn} written by {book.author} published in the year {book.year}")
                return render_template('books.html', row=query.all(), email=session['email'])
            else:
                flash(
                    "there are no books available with the specified details,try with more specific details")
                return render_template('search.html', email=session['email'])
        except SQLAlchemyError as e:
            print(e)
            return render_template('fail.html', path='./static/css/style.css')
        finally:
            db.close()
    elif isbn == "" and title == "" and author != "":
        try:
            db = scoped_session(sessionmaker(bind=engine))
            author = '%'+author+'%'
            session['author'] = author
            session['isbn'] = None
            session['title'] = None
            query = db.query(Books).filter(Books.author.ilike(author))
            if query != None:
                # r = query.all()
                # print(r)
                # for book in r:
                #     print(f"added{book.title} with number {book.isbn} written by {book.author} published in the year {book.year}")
                return render_template('books.html', row=query.all(), email=session['email'])
            else:
                flash(
                    "there are no books available with the specified details,try with more specific details")
                return render_template('search.html', email=session['email'])
        except SQLAlchemyError as e:
            print(e)
            return render_template('fail.html', path='./static/css/style.css')
        finally:
            db.close()
    elif isbn != "" and title != "" and author == "":
        try:
            db = scoped_session(sessionmaker(bind=engine))
            title = '%'+title+'%'
            isbn = '%'+isbn+'%'
            session['title'] = title
            session['isbn'] = isbn
            session['author'] = None
            query = db.query(Books).filter(
                or_(Books.title.ilike(title), Books.isbn.ilike(isbn)))
            if query != None:
                # r = query.all()
                # print(r)
                # for book in r:
                #     print(f"added{book.title} with number {book.isbn} written by {book.author} published in the year {book.year}")
                return render_template('books.html', row=query.all(), email=session['email'])
            else:
                flash(
                    "there are no books available with the specified details,try with more specific details")
                return render_template('search.html', email=session['email'])
        except SQLAlchemyError as e:
            print(e)
            return render_template('fail.html', path='./static/css/style.css')
        finally:
            db.close()
    elif isbn != "" and title == "" and author != "":
        try:
            db = scoped_session(sessionmaker(bind=engine))
            isbn = '%'+isbn+'%'
            author = '%'+author+'%'
            session['author'] = author
            session['isbn'] = isbn
            session['title'] = None
            query = db.query(Books).filter(
                or_(Books.isbn.ilike(isbn), Books.author.ilike(author)))
            if query != None:
                # r = query.all()
                # print(r)
                # for book in r:
                #     print(f"added{book.title} with number {book.isbn} written by {book.author} published in the year {book.year}")
                return render_template('books.html', row=query.all(), email=session['email'])
            else:
                flash(
                    "there are no books available with the specified details,try with more specific details")
                return render_template('search.html', email=session['email'])
        except SQLAlchemyError as e:
            print(e)
            return render_template('fail.html', path='./static/css/style.css')
        finally:
            db.close()
    elif isbn == "" and title != "" and author != "":
        try:
            db = scoped_session(sessionmaker(bind=engine))
            title = '%'+title+'%'
            author = '%'+author+'%'
            session['title'] = title
            session['author'] = isbn
            session['isbn'] = None
            query = db.query(Books).filter(
                or_(Books.title.ilike(title), Books.author.ilike(author)))
            if query != None:
                # r = query.all()
                # print(r)
                # for book in r:
                #     print(f"added{book.title} with number {book.isbn} written by {book.author} published in the year {book.year}")
                return render_template('books.html', row=query.all(), email=session['email'])
            else:
                flash(
                    "there are no books available with the specified details,try with more specific details")
                return render_template('search.html', email=session['email'])
        except SQLAlchemyError as e:
            print(e)
            return render_template('fail.html', path='./static/css/style.css')
        finally:
            db.close()
    else:
        try:
            db = scoped_session(sessionmaker(bind=engine))
            isbn = '%'+isbn+'%'
            title = '%'+title+'%'
            author = '%'+author+'%'
            session['title'] = title
            session['isbn'] = isbn
            session['author'] = author
            query = db.query(Books).filter(or_(Books.title.ilike(
                title), Books.author.ilike(author), Books.isbn.ilike(isbn)))
            if query != None:
                r = query.all()
                print(r)
                for book in r:
                    print(
                        f"added{book.title} with number {book.isbn} written by {book.author} published in the year {book.year}")
                return render_template('books.html', row=query.all(), email=session['email'])
            else:
                flash(
                    "there are no books available with the specified details,try with more specific details")
                return render_template('search.html', email=session['email'])
        except SQLAlchemyError as e:
            print(e)
            return render_template('fail.html', path='./static/css/style.css')
        finally:
            db.close()


@app.route("/searchtest")
def searchtest():
    if 'email' in session:
        return render_template('search.html', email=session['email'])
    return render_template('index.html', email=None)


@app.route("/booksearch/<string:isbn>")
def booksearch(isbn):
    if 'email' in session:
        db = scoped_session(sessionmaker(bind=engine))
        try:
            # If table don't exist, Create.
            if not engine.dialect.has_table(engine, "REVIEWS"):
                Reviews.__table__.create(bind=engine, checkfirst=True)
            # query = db.query(Books).filter(Books.isbn==isbn)
            query = db.query(Books).filter(Books.isbn == isbn)
            if query != None:
                # r = query.all()
                # print(r)
                # for book in r:
                #     print(f"added{book.title} with number {book.isbn} written by {book.author} published in the year {book.year}")
                booksquery = db.query(Reviews).filter(Reviews.isbn == isbn)
                print(booksquery)
                res = requests.get("https://www.goodreads.com/book/review_counts.json",
                                   params={"key": " iNR9v978MfG0fz9pCcaFQ", "isbns": isbn})
                data = res.text
                parsed = json.loads(data)
                print(parsed)
                res = {}
                for i in parsed:
                    for j in (parsed[i]):
                        res = j
                return render_template('bookdetails.html', book=query.first(), email=session['email'], res=res, isbn=isbn, review=booksquery.all())
            else:
                flash(
                    "there are no books available with the specified details,try with more specific details")
                return render_template('search.html', email=session['email'])
        except SQLAlchemyError as e:
            print(e)
            return render_template('fail.html', path='./static/css/style.css')
        finally:
            db.close()


@app.route("/review/<string:isbn>", methods=["POST"])
def review(isbn):
    email = session['email']
    print(email)
    now = datetime.now()
    rating = request.form['rating']
    review = request.form.get("review")
    fname = session['fname']
    print(fname)
    author = session['author']
    print("author =", session['author'])
    title = session['title']
    print("title =", session['title'])
    try:
        db = scoped_session(sessionmaker(bind=engine))
        query = db.query(Reviews).filter(Reviews.email == email)

        if query != None:
            rbooks = []
            for r in query.all():
                rbooks.append(r.isbn)
            bquery = book_query(isbn, author, title)
            if isbn not in rbooks:
                # query = db.query(Users).filter(Users.email==email)
                row = Reviews(email=email, fname=fname, review=review,
                              date=now, isbn=isbn, rating=rating)
                db.add(row)
                db.commit()
                flash("Review Submitted")
                return render_template('books.html', row=bquery, email=session['email'])
            else:
                flash("You already reviewed the book, try to review another book")
                return render_template('books.html', row=bquery, email=session['email'])
        else:
            row = Reviews(email=email, fname=fname, review=review,
                          date=now, isbn=isbn, rating=rating)
            db.add(row)
            db.commit()
            bquery = book_query(isbn, author, title)
            flash("Review Submitted")
            return render_template('books.html', row=bquery, email=session['email'])
    except SQLAlchemyError as e:
        print(e)
        return render_template('fail.html', path='./static/css/style.css')
    finally:
        db.close()


def book_query(isbn, author, title):
    try:
        db = scoped_session(sessionmaker(bind=engine))
        bquery = None
        if session['title'] != None and session['isbn'] != None and session['author'] != None:
            bquery = db.query(Books).filter(or_(Books.title.ilike(
                title), Books.author.ilike(author), Books.isbn.ilike(isbn)))
        elif session['title'] != None and session['author'] != None:
            bquery = db.query(Books).filter(
                or_(Books.title.ilike(title), Books.author.ilike(author)))
        elif session['author'] != None and session['isbn'] != None:
            bquery = db.query(Books).filter(
                or_(Books.isbn.ilike(isbn), Books.author.ilike(author)))
        elif session['title'] != None and session['isbn'] != None:
            bquery = db.query(Books).filter(
                or_(Books.title.ilike(title), Books.isbn.ilike(isbn)))
        elif session['isbn'] != None:
            bquery = db.query(Books).filter(Books.isbn.ilike(isbn))
        elif session['title'] != None:
            bquery = db.query(Books).filter(Books.title.ilike(title))
        else:
            bquery = db.query(Books).filter(Books.author.ilike(author))
    except SQLAlchemyError as e:
        print(e)
        return render_template('fail.html', path='./static/css/style.css')
    finally:
        db.close()

    if bquery == None:
        return None

    return bquery.all()


@app.route("/login", methods=["POST"])
def login():
    return render_template('login.html', path='./static/css/style.css')


@app.route("/login_form")
def login_form():
    session.clear()
    session.pop('email', None)
    return render_template('index.html', path='./static/css/style.css', email=None)


@app.route("/main")
def main():
    if 'email' in session:
        try:
            db = scoped_session(sessionmaker(bind=engine))
            query = db.query(Users).order_by(Users.date)
            return render_template('main.html', row=query.all())
        except SQLAlchemyError as e:
            print(e)
            return render_template('fail.html', path='./static/css/style.css')
        finally:
            db.close()
    else:
        return render_template('index.html', email=None)


if __name__ == "__main__":
    # app.secret_key = "#RR#"
    app.run(debug=True)
    # Session(app)
