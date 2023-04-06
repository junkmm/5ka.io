import requests
import json
from models.apps_url import AppUrlModel
from db import db
from models.teams import TeamModel
import os

KIBANA_URL=os.getenv("KIBANA_URL")
KIBANA_USER=os.getenv("KIBANA_USER")
KIBANA_PWD=os.getenv("KIBANA_PWD")

def kibana_user_create(user_id,user_pwd,team_name):
    url = f"{KIBANA_URL}/_security/user/{user_id}?pretty"
    data = {
        "password" : user_pwd,
        "roles" : f"{team_name}"
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, auth=(KIBANA_USER, KIBANA_PWD), headers=headers, json=data)
    return