import os
import sys

from flask import Flask,render_template,request,session
from flask_session import Session
from datetime import datetime

# from flask.ext.session import Session
from sqlalchemy import * #create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import * #scoped_session, sessionmaker

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
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
# engine = create_engine("postgres://lcrwacesatfmjm:7775a710b16c87a20154bc9df86aceb643b9cc6afbb29c781bc068f25f19df21@ec2-54-247-71-245.eu-west-1.compute.amazonaws.com:5432/d6r9sefsl5m5i3")
# db = scoped_session(sessionmaker(bind=engine))
print(engine.table_names(),file=sys.stdout)

Base = declarative_base()
class Users(Base):
    __tablename__ = "USERS"
    email = Column(String, primary_key=True, nullable=False)
    fname = Column(String)
    lname = Column(String)
    pwrd = Column(String)
    date = Column(DateTime)

@app.route("/")
def index():
    return "Project 1: TODO"


@app.route("/register")
def register():
    if not engine.dialect.has_table(engine, "USERS"):  # If table don't exist, Create.
        # db_engine = connect_db()
        # path='./static/css/styles.min.css'
        Users.__table__.create(bind=engine, checkfirst=True)
    return render_template('register.html')



@app.route("/registration",methods=["POST"])
def registration():
    db = scoped_session(sessionmaker(bind=engine))
    rfname=request.form.get("first_name")
    rlname=request.form.get("last_name")
    remail=request.form.get("email")
    rpassword=request.form.get("password")
    rcpassword=request.form.get("confirm_password")
    if rpassword == rcpassword:
        # data = {'a': 5566, 'b': 9527, 'c': 183}
        try:
            # for _key, _val in data.items():
            now = datetime.now()
            # formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
            row = Users(email=remail,fname=rfname,lname=rlname,pwrd=rpassword,date=now)
            db.add(row)
            db.commit()
        except SQLAlchemyError as e:
            print(e)
            return render_template('fail.html',path='./static/css/styles.min.css')
        finally:
            db.close()
            return render_template('success.html',path='./static/css/styles.min.css')
    else:
        return "confirmation password does not match with the Entered password, Try again"

    print(remail+" , "+rfname+" , "+rlname,file=sys.stdout)
    print(remail+" , "+rfname+" , "+rlname, file=sys.stderr)

    return remail+" , "+rfname+" , "+rlname



@app.route("/main")
def data():
    try:
        db = scoped_session(sessionmaker(bind=engine))
        query = db.query(Users).order_by(Users.date)
        return render_template('main.html',row = query.all())
    except SQLAlchemyError as e:
        print(e)
        return render_template('fail.html',path='./static/css/styles.min.css')
    finally:
        db.close()


if __name__ == "__main__":
    app.run(debug=True)
