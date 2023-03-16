from flask.views import MethodView
from flask import request
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from flask_smorest import Blueprint, abort
from db import db
from models import TeamModel
from service.jenkins import create_team_and_call_jenkins_api

blp = Blueprint("team", __name__, description="team blueprint")

# 팀 생성
@blp.route("/api/v1/team")
class Team(MethodView):
    def post(self):
        team_data = request.json
        # 입력 받은 data 검증하기 name 필드가 없으면 안됨, 값은 증명 못함(빈 칸으로 입력해도 생성됨).
        if "name" not in team_data:
            abort(400, message="Request data is missing")
        # team 변수에 request받은 team_data를 TeamModel전달 후 저장?
        team = TeamModel(**team_data)
        try:
            db.session.add(team)
            db.session.commit()
            """
            team 생성 시 Jenkins Item Role을 생성하는 코드, 팀은 고정으로 박아둘 거기 떄문에 사용 안함
            create_team_and_call_jenkins_api(team_data["name"])
            team_q = TeamModel.query.filter(TeamModel.name == team_data["name"]).first()
            """
            
        # unique = true 여서 기존 data가 있으면 에러
        except IntegrityError:
            abort(400, message="A Team with that name already exists.")
        except SQLAlchemyError:
            abort(500, message="An error occured creating the Team")

        return {"message":"Team Created succesfully","team_name":team.name,"team_id":team_q.id}, 201