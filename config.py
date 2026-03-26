import os

class Config:

    SECRET_KEY = os.getenv("SECRET_KEY", "090806")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+mysqlconnector://root:xLnWyOjMHoSwYjCfNQjqciACrbFSvzar@shuttle.proxy.rlwy.net:52430/railway"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False