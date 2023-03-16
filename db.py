from flask import abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import requests


db = SQLAlchemy()

# 최초 실행 시 dev, ops 팀이 없으면 생성하는 기능
def create_default_team():
    from models import TeamModel 
    teams = TeamModel.query.all()
    team_names = [team.name for team in teams]
    if "dev" not in team_names:
        team_q = TeamModel(name='dev')
        db.session.add(team_q)
        db.session.commit()
    if "ops" not in team_names:
        team_q = TeamModel(name='ops')
        db.session.add(team_q)
        db.session.commit()