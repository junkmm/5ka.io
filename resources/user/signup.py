from flask.views import MethodView
from flask import request
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.hash import pbkdf2_sha256
from db import db
from models import UserModel

blp = Blueprint("signup", __name__, description="sign up user")

@blp.route("/api/v1/signup")
class Team(MethodView):
    def post(self):
        signup_data = request.json
        # 입력 받은 data 검증하기 user_id, password, team_id, name, email 필드에
        if "user_id" not in signup_data or "password" not in  signup_data or "team_id" not in signup_data or "name" not in signup_data or "email" not in signup_data:
            abort(400, message="Request data is missing")
        
        user = UserModel(
            user_id = signup_data["user_id"],
            name = signup_data["name"],
            password = pbkdf2_sha256.hash(signup_data["password"]),
            email = signup_data["email"],
            team_id = signup_data["team_id"]
        )
        
        try:
            db.session.add(user)
            db.session.commit()
        # unique = true 여서 기존 data가 있으면 에러
        except IntegrityError:
            abort(400, message="A Team with that name already exists.")
        except SQLAlchemyError:
            abort(500, message="An error occured creating the Team")

        return {"message":"User Created succesfully"}, 201