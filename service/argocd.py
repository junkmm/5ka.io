import requests
import json
from db import db
from flask_smorest import abort
from models import TeamModel,AppModel,AppUrlModel
import os

ARGO_URL = os.getenv("ARGO_URL")
ARGO_TOKEN = os.getenv("ARGO_TOKEN")
headers = {
    "Content-Type": "application/json",
    "Authorization": ARGO_TOKEN
}

def create_argocd_application(app_name, app_type, team, app_id):
    app = AppModel.query.filter(AppModel.name == app_name).first()
    appurl = AppUrlModel.query.filter(AppUrlModel.app_id == app.id).first()
    qteam = TeamModel.query.filter(TeamModel.name == team).first()

    team_cluster_endpoint_name = qteam.k8s_cluster_name_for_argo
    helm_url = appurl.gitlab_helm

    xml_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resource", "argo_application_template.json")
    with open(xml_file_path, "r") as file:
        data = json.load(file)

    data["metadata"]["name"] = app_name
    data["spec"]["destination"]["name"] = team_cluster_endpoint_name
    data["spec"]["destination"]["namespace"] = app_name
    data["spec"]["source"]["repoURL"] = f"{helm_url}.git"
    data["spec"]["source"]["helm"]["parameters"][0]["value"] = app_type
    data["spec"]["project"] = team

    create_application_url = f"{ARGO_URL}/api/v1/applications"
    response = requests.post(create_application_url, headers=headers, json=data, verify=False)

    # AppUrlModel에 저장
    argocd_url = f"{ARGO_URL}/applications/argocd/{app_name}?view=tree&resource="
    app_url_record = AppUrlModel.query.filter(AppUrlModel.app_id == app_id).first()
    app_url_record.argocd = argocd_url
    db.session.commit()

def argoce_app_depoloy(app_name):
    deploy_app_url = f"{ARGO_URL}/api/v1/applications/{app_name}/sync"
    response = requests.post(deploy_app_url, headers=headers, verify=False)
    if response.status_code != 200:
        abort(400, message="Deploy Error")
    return {"message":"Deploy successfully"}, 201