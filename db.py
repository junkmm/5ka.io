from flask import abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import requests
import os

db = SQLAlchemy()

# 최초 실행 시 dev, ops 팀이 없으면 생성하는 기능
def create_default_team():
    from models import TeamModel 
    dev_cluster = os.getenv("DEV_CLUSTER_NAME")
    ops_cluster = os.getenv("OPS_CLUSTER_NAME")

    teams = TeamModel.query.all()
    team_names = [team.name for team in teams]
    if "dev" not in team_names:
        team_q = TeamModel(name='dev',k8s_cluster_name_for_argo=dev_cluster)
        db.session.add(team_q)
        db.session.commit()
    if "ops" not in team_names:
        team_q = TeamModel(name='ops',k8s_cluster_name_for_argo=ops_cluster)
        db.session.add(team_q)
        db.session.commit()