from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import cloudinary
from flask_login import LoginManager

app = Flask(__name__)

app.secret_key = '$@C$cC@$C@$C@$@BL$@$@V$33v43242c41c41#@#$@CK@C'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/test_bsm_db?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['PAGE_SIZE'] = 8
app.config['COMMENT_SIZE'] = 3

cloudinary.config(
    cloud_name='dtnhdndxh',
    api_key='137595884788452',
    api_secret='GUlWOUys-JuLp8onAR7mgNNAX3g'
)
db = SQLAlchemy(app=app)
login = LoginManager(app=app)
