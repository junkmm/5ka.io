from flask.views import MethodView
from flask import jsonify, request
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask_smorest import Blueprint, abort
from db import db
from models import ProjectModel, TeamModel, AppModel
from models.users import UserModel
from service.jenkins import jenkins_create_folder

blp = Blueprint("project", __name__, description="project Operation")

@blp.route("/api/v1/project")
class ProjectList(MethodView):
    def post(self):
        project_data = request.json

        # 입력 받은 data 검증하기 name, type, description, team_id, user_id 필드 있는지 검사
        if "name" not in project_data or "description" not in  project_data or "user_id" not in project_data:
            abort(400, message="Request data is missing")
        if not project_data["name"]:
            abort(400, message="blank Project")
        user = UserModel.query.filter(UserModel.user_id == project_data["user_id"]).first()

        # User변수에 입력받은 값 대입, password는 암호화 적용하기.
        project = ProjectModel(
            name = project_data["name"],
            description = project_data["description"],
            user_id = user.id,
            team_id = user.team_id
        )
        
        # DB에 저장하기
        try:
            db.session.add(project)
            db.session.commit()
            """
            #Jenkins Folder(Project) 생성, # Jenkins 프로젝트 개념은 사용하지 않기로 해서 주석 처리
            name = project_data["name"]
            team = TeamModel.query.filter(TeamModel.id == project_data["team_id"]).first()
            jenkins_create_folder(name,team.name)
            """
        # unique = true 여서 기존 data가 있으면 에러
        except IntegrityError:
            abort(400, message="A project name already exists.")
        except SQLAlchemyError:
            abort(500, message="An error occured creating the Team")
        return {"message":"Project Created successfully"}, 201

@blp.route("/api/v1/projects/<string:team_id>")
class Project(MethodView):
    def get(self, team_id):
        projects = ProjectModel.query.filter_by(team_id=team_id).all()
        projects_json = []
        team = TeamModel.query.filter(TeamModel.id==team_id).first()
        for project in projects:
            project_data = project.serialize()
            app_count = db.session.query(AppModel).filter(AppModel.project_id == project.id).count()
            project_data["app_count"] = app_count
            projects_json.append(project_data)

        result_json = []
        result_json.append(
                {
                    "team_id":team_id,
                    "team_name":team.name,
                    "projects":list(projects_json)
                }
        )
        return jsonify(result_json[0])