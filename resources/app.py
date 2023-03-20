from flask.views import MethodView
from flask import jsonify, request
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask_smorest import Blueprint, abort
from db import db
from models import ProjectModel, AppModel, UserModel, AppUrlModel
from models.teams import TeamModel
from service.gitlab import gitlab_create_application_from_fork
from service.jenkins import jenkins_create_application_pipeline

blp = Blueprint("app", __name__, description="app Operation")


@blp.route("/api/v1/app")
class AppCreate(MethodView):
    def post(self):
        app_data = request.json

        # 입력 받은 data 검증하기 name, type, description, team_id, user_id 필드 있는지 검사
        if "name" not in app_data or "description" not in  app_data or "type" not in  app_data or "project_id" not in app_data or "user_id" not in app_data:
            abort(400, message="Request data is missing")
        if not app_data["name"]:
            abort(400, message="blank Project")
        
        # User변수에 입력받은 값 대입, password는 암호화 적용하기.
        app = AppModel(**app_data)
        
        # DB에 저장하기
        try:
            db.session.add(app)
            db.session.commit()
            #gitlab_repositort_fork
            user = UserModel.query.filter(UserModel.id == app_data["user_id"]).first()
            gitlab_create_application_from_fork(app_data["type"], app_data["name"], user.team_id, app.id)
            #Jenkins pipeline create
            appurl = AppUrlModel.query.filter(AppUrlModel.app_id == app.id).first()
            team = TeamModel.query.filter(TeamModel.id == user.team_id).first()
            jenkins_create_application_pipeline(team.name,app_data["name"],appurl.gitlab,app.id)
        # unique = true 여서 기존 data가 있으면 에러
        except IntegrityError:
            abort(400, message="A app Intergrity already exists.")
        except SQLAlchemyError:
            abort(500, message="An error occured creating the Team")
        return {"message":"Application Created succesfully"}, 201

@blp.route("/api/v1/apps/<string:project_id>")
class App(MethodView):
    def get(self, project_id):
        apps = AppModel.query.filter_by(project_id=project_id).all()
        apps_json = [app.serialize() for app in apps]
        return jsonify(apps_json)