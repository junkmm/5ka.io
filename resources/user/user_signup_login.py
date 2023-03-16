from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.hash import pbkdf2_sha256
from db import db
from models import UserModel, TeamModel
from service.jenkins import create_jenkins_user, role_bind_jenkins_user

blp = Blueprint("user", __name__, description="user Operation")
# 회원 가입
@blp.route("/api/v1/signup")
class Team(MethodView):
    def post(self):
        signup_data = request.json
        # 입력 받은 data 검증하기 user_id, password, team_id, name, email 필드 있는지 검사
        if "user_id" not in signup_data or "password" not in  signup_data or "team_id" not in signup_data or "name" not in signup_data or "email" not in signup_data:
            abort(400, message="Request data is missing")
        if not signup_data["user_id"] or not signup_data["password"]:
            abort(400, message="id or password is blank.")
        
        # User변수에 입력받은 값 대입, password는 암호화 적용하기.
        user = UserModel(
            user_id = signup_data["user_id"],
            name = signup_data["name"],
            password = pbkdf2_sha256.hash(signup_data["password"]),
            email = signup_data["email"],
            team_id = signup_data["team_id"]
        )
        
        # DB에 저장하기
        try:
            db.session.add(user)
            db.session.commit()

            # Jenkins 사용자 추가하기
            create_jenkins_user(user.user_id, signup_data["password"], user.email, user.name)
            # Jenkins Role bind
            team = TeamModel.query.filter(TeamModel.id == signup_data["team_id"]).first()
            role_bind_jenkins_user(user.name,team.name)

        # unique = true 여서 기존 data가 있으면 에러
        except IntegrityError:
            abort(400, message="A name already exists.")
        except SQLAlchemyError:
            abort(500, message="An error occured creating the Team")

        return {"message":"User Created successfully"}, 201
# 로그인
@blp.route("/api/v1/login")
class Team(MethodView):
    def post(self):
        login_data = request.json
        # 입력 받은 data 검증하기 user_id, password 필드 검사하기
        if "user_id" not in login_data or "password" not in  login_data:
            abort(400, message="Request data is missing")

        if not login_data["user_id"] or not login_data["password"]:
            abort(400, message="id or password is blank.")

        user = UserModel.query.filter(UserModel.user_id == login_data["user_id"]).first()

        # 로그인 성공시
        if user and pbkdf2_sha256.verify(login_data["password"], user.password):
            return {"message":"Login successfully","user_id":user.id,"team_id":user.team_id}, 201

        # 로그인 실패 시
        abort(401, message="Invalid credentials.")