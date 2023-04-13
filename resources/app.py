from flask.views import MethodView
from flask import jsonify, request
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask_smorest import Blueprint, abort
from db import db
from models import ProjectModel, AppModel, UserModel, AppUrlModel
from models.teams import TeamModel
from service.gitlab import gitlab_create_application_from_fork
from service.jenkins import jenkins_create_application_pipeline, jenkins_buildwithparameter_pipeline
from service.argocd import argoce_app_depoloy

blp = Blueprint("app", __name__, description="app Operation")


@blp.route("/api/v1/app")
class AppCreate(MethodView):
    # /ap1/v1/app post 요청 처리
    # web console에서 application 생성하기
    def post(self):
        app_data = request.json

        # 입력 받은 data 검증하기 name, type, description, team_id, user_id 필드 있는지 검사
        if "name" not in app_data or "description" not in  app_data or "type" not in  app_data or "project_id" not in app_data or "user_id" not in app_data:
            abort(400, message="Request data is missing")
        if not app_data["name"]:
            abort(400, message="blank Project")
        
        # user_id 의 id(fk)값을 저장하기 위해 쿼리 후 객체 저장
        u = UserModel.query.filter(UserModel.user_id == app_data["user_id"]).first()
        project = ProjectModel.query.filter(ProjectModel.id == app_data["project_id"]).first()

        # 만약 A팀의 프로젝트에서 B 유저가 애플리케이션을 생성한다고 했을 때
        # B 유저가 A팀에 소속되었는지 검증한다. 만약 팀이 다른경우 Auth Error를 뱉는다.
        if u.team_id != project.team_id:
            abort(400,message="Auth Error")

        # app 변수에 DB저장 데이터 저장
        app = AppModel(
            name=app_data["name"],
            type=app_data["type"],
            description= app_data["description"],
            project_id= app_data["project_id"],
            user_id=u.id
        )
        
        # DB에 저장하기
        try:
            db.session.add(app)
            db.session.commit()
            # 깃랩 애플리케이션 생성 함수 호출
            gitlab_create_application_from_fork(app_data["type"], app_data["name"], u.team_id, app.id)
            # 젠킨스 파이프라인 생성 함수 호출
            appurl = AppUrlModel.query.filter(AppUrlModel.app_id == app.id).first()
            team = TeamModel.query.filter(TeamModel.id == u.team_id).first()
            jenkins_create_application_pipeline(team.name,app_data["name"],appurl.gitlab_source,app.id)
        # unique = true 여서 기존 data가 있으면 에러
        except IntegrityError:
            abort(400, message="A app Intergrity already exists.")
        except SQLAlchemyError:
            abort(500, message="An error occured creating the Team")
        return {"message":"Application Created successfully"}, 201


@blp.route("/api/v1/apps/<string:project_id>")
class App(MethodView):
    # project에 상속된 application 목록 반환하기
    def get(self, project_id):
        apps = AppModel.query.filter_by(project_id=project_id).all()
        apps_json = []
        for app in apps:
            app_data = app.serialize()
            app_data["user_id"] = UserModel.query.filter_by(id=app.user_id).first().user_id
            apps_json.append(app_data)

        project = ProjectModel.query.filter(ProjectModel.id == project_id).first()
        team = TeamModel.query.filter(project.team_id==TeamModel.id).first()
        result_json = []
        result_json.append(
            {
                "team_id": team.id,
                "team_name": team.name,
                "project_id":project_id,
                "project_name":project.name,
                "applications":list(apps_json)
            }
        )
        for app_json in result_json[0]["applications"]:
            del app_json["project_id"]

        return jsonify(result_json[0])


@blp.route("/api/v1/argocd/<string:app_id>")
class ArgocdDeploy(MethodView):
    # argocd application 배포하기
    def get(self, app_id):
        app = AppModel.query.filter(AppModel.id == app_id).first()
        if app is not None:
            return argoce_app_depoloy(app.name)
        else:
            abort (400,message="Application Not found")
        

@blp.route("/api/v1/jenkins/<string:app_id>")
class JenkinsBuild(MethodView):
    # jenkins job 실행시키기
    def get(self, app_id):
        app = AppModel.query.filter(AppModel.id == app_id).first()
        # get으로 요청받은 Application이 DB에 있는지 확인, 있으면 해당 젠킨스 파이프라인 빌드 진행
        if app is not None:
            project = ProjectModel.query.filter(ProjectModel.id == app.project_id).first()
            team = TeamModel.query.filter(TeamModel.id == project.team_id).first()
            jenkins_buildwithparameter_pipeline(team.name,app.name)
            return {"message":"Build successfully"}, 201
        else:
            abort (400,message="Application Not found")

@blp.route("/api/v1/application/<string:app_id>")
class AppList(MethodView):
    # application 상세 정보 반환하기
    def get(self, app_id):
        app = AppModel.query.filter(AppModel.id == app_id).first()
        # gitlab_source url, gitlab_helm url, jenkins_url, argocd_url, grafana_url, kibana_url
        if app is not None:
            appurl = AppUrlModel.query.filter(AppUrlModel.app_id == app_id).first()
            project = ProjectModel.query.filter(ProjectModel.id == app.project_id).first()
            team = TeamModel.query.filter(TeamModel.id == project.team_id).first()
            result_json = []
            result_json.append(
                {
                    "team_id": team.id,
                    "team_name": team.name,
                    "project_id":project.id,
                    "project_name":project.name,
                    "gitlab_source_url":appurl.gitlab_source,
                    "gitlab_helm_url":appurl.gitlab_helm,
                    "jenkins_url":appurl.jenkins,
                    "argocd_url":appurl.argocd,
                    "grafana_url":appurl.grafana,
                    "kibana_url":appurl.kibana
                }
            )
            return jsonify(result_json[0])
        else:
            abort (400,message="Application Not found")