from flaskext.mysql import MySQL
from flask import Flask


app = Flask(__name__)

# MySQL configurations
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'ORGA'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'orga'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
app.config['MYSQL_DATABASE_PORT'] = int('3306')
app.config['URL_IMAGE'] = 'http://159.65.169.194:8003'


mysql.init_app(app)
