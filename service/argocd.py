import requests
import json
from db import db
from models import TeamModel,AppModel,AppUrlModel
import os

ARGO_URL = os.getenv("ARGO_URL")
ARGO_TOKEN = os.getenv("ARGO_TOKEN")

def create_argocd_application(app_name, app_type, team):
    app = AppModel.query.filter(AppModel.name == app_name).first()
    appurl = AppUrlModel.query.filter(AppUrlModel.app_id == app.id).first()
    qteam = TeamModel.query.filter(TeamModel.name == team).first()

    team_cluster_endpoint_name = qteam.k8s_cluster_name_for_argo
    helm_url = appurl.gitlab_helm

    headers = {
        "Content-Type": "application/json",
        "Authorization": ARGO_TOKEN
    }

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
    print(json.dumps(data))
    response = requests.post(create_application_url, headers=headers, json=data, verify=False)
    request = response.request

    curl_cmd = f"curl -X {request.method}"

    for header, value in request.headers.items():
        curl_cmd += f" -H '{header}: {value}'"

    if request.body:
        curl_cmd += f" -d '{request.body.decode('utf-8')}'"

    curl_cmd += f" '{request.url}'"

    print(curl_cmd)