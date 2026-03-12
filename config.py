import os

class Config:
    SECRET_KEY = '090806'
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:090806@localhost:3306/veza_portal_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False