import csv
import os
from flask import Flask, render_template, request, session
from pymodel import *
from sqlalchemy import create_engine
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy import or_
from sqlalchemy import desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL

# Check for environment variable
from sqlalchemy.testing import db

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")
app = Flask(__name__)
engine = create_engine(os.getenv("DATABASE_URL"))
Base = declarative_base()
class Books(Base):
    __tablename__ = "BOOKS"
    isbn = Column(String, primary_key=True, nullable=False)
    title = Column(String)
    author = Column(String)
    year = Column(Integer)

# Configure session to use filesystem
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
if not engine.dialect.has_table(engine, "BOOKS"):
    Books.__table__.create(bind=engine, checkfirst=True)

db.init_app(app)
print('called main')


f = open("./static/books.csv")
reader = csv.reader(f)
next(reader)

def main():
    print('called main')
    db.create_all()
    f = open("./static/books.csv")
    reader = csv.reader(f)
    next(reader)


Session = sessionmaker()
Session.configure(bind=engine)
session = Session()
objects = []
try:
    # i = 0
    for isbn, title, author, year in reader:
        book = Books(isbn=isbn, title=title, author=author, year=year)
        db.session.add(book)
        print(
            f"added{book.title} with number {book.isbn} written by {book.author} published in the year {book.year}")
        # if i==5:
        #     break
        book = Books(isbn=isbn, title=title, author=author, year=year)
        objects.append(book)
        # i += 1
    session.bulk_save_objects(objects)
    # session.add(book)
    # print(f"added{book.title} with number {book.isbn} written by {book.author} published in the year {book.year}")
    print('sessoin before commited')
    db.session.commit()
    session.commit()
    print('sessoin commited')

    if __name__ == "__main__":
        with app.app_context():
            main()
except SQLAlchemyError as e:
    print(e)
finally:
    session.close()