from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.environ.get('TOKEN')

DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')

#Heroku web-socket
# URL_APP = os.environ.get('URL_APP')