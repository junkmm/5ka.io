from flask import Flask  # 서버 구현을 위한 Flask 객체 import
from flask_smorest import Api  # Api 구현을 위한 Api 객체 import
from resources.user_signup_login import blp as SignupBlueprint
from resources.team import blp as TeamBlueprint
from resources.project import blp as Projectblueprint
from resources.app import blp as Appblueprint
from db import create_default_team, db
import models

def create_app():
    app = Flask(__name__)  # Flask 객체 선언, 파라미터로 어플리케이션 패키지의 이름을 넣어줌.
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "k5s REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://dbuser:1234@1.220.201.109:33306/5ka_jun'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    api = Api(app)  # Flask 객체에 Api 객체 등록

    api.register_blueprint(SignupBlueprint)
    api.register_blueprint(TeamBlueprint)
    api.register_blueprint(Projectblueprint)
    api.register_blueprint(Appblueprint)
    

    db.init_app(app)

    with app.app_context():
        db.create_all()
        create_default_team()
    return app