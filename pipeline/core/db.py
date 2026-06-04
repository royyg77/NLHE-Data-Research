# import os
# import psycopg2
# from dotenv import load_dotenv

# load_dotenv()  # reads your .env file into the environment

# def get_connection():
#     return psycopg2.connect(
#         host=os.getenv("DB_HOST"),
#         port=os.getenv("DB_PORT"),
#         dbname=os.getenv("DB_NAME"),
#         user=os.getenv("DB_USER"),
#         password=os.getenv("DB_PASSWORD"),
#     )

##### Using sqlalchemy instead of psycopg2 

import os
from sqlalchemy import create_engine, URL
from dotenv import load_dotenv
# from urllib.parse import quote

load_dotenv()

# def get_engine():
#     user = os.getenv("DB_USER")
#     password = quote(os.getenv("DB_PASSWORD"))
#     host = os.getenv("DB_HOST")
#     port = os.getenv("DB_PORT")
#     dbname = quote(os.getenv("DB_NAME"))
#     url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
#     return create_engine(url)

def get_engine():
    url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
    )
    return create_engine(url)