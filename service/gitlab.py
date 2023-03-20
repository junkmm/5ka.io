import requests
import json
from models.apps_url import AppUrlModel
from db import db
from models.teams import TeamModel

GITLAB_URL = 'http://1.220.201.109:30835'
GITLAB_TOKEN = 'glpat-3FnTXSda_PsrxxdYGhmQ'

def gitlab_create_user_and_join_group(name, email, password, group_name):

    headers = {"Content-Type": "application/json", "PRIVATE-TOKEN": GITLAB_TOKEN}

    # GitLab 사용자 생성하기
    data = {'name': name, 'username': name, 'email': email, 'password': password, "skip_confirmation": True}
    response = requests.post(f'{GITLAB_URL}/api/v4/users', headers=headers, json=data)

    if response.status_code != 201:
        print('Failed to create user.')
        print(f"User creation failed with status code: {response.status_code}, and content: {response.content}")
        return

    # group_name의 GID 조회하기
    user_id = response.json()['id']
    response = requests.get(f'{GITLAB_URL}/api/v4/groups?search={group_name}', headers=headers)

    if response.status_code != 200:
        print(f"Failed to retrieve group {group_name} information.")
        return

    try:
        group_id = response.json()[0]['id']
    except IndexError:
        print(f"Group with name {group_name} does not exist.")
        return

    # 사용자 그룹에 추가하기
    data = {'user_id': user_id, 'access_level': 30}
    response = requests.post(f'{GITLAB_URL}/api/v4/groups/{group_id}/members', headers=headers, json=data)

    if response.status_code == 201:
        print('User added to group successfully!')
    else:
        print('Failed to add user to group.')

def gitlab_create_application_from_fork(type,app_name,team_id,app_id):
    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
    if type == "spring":
        # GitLab "Spring Template" 프로젝트 조회하여 ID 획득
        # spring이면 template 이름이 Sprint_Template 여야 함.
        url = f"{GITLAB_URL}/api/v4/projects?search=Spring_Template"
        response = requests.get(url, headers=headers)
        project_id = response.json()[0]['id']
    else:
        # 다른 타입일 경우, 프로젝트 ID 직접 입력
        project_id = "your_project_id_here"

    # team_id로 team명 추출하기
    team = TeamModel.query.filter(TeamModel.id == team_id).first()
    team_name = team.name
    # Fork 요청 보내기
    url = f"{GITLAB_URL}/api/v4/projects/{project_id}/fork"
    data = {"namespace_path": team_name+"/source", "name": app_name, "path": app_name}
    response = requests.post(url, headers=headers, data=data)


    new_app_url = AppUrlModel(
        gitlab=f"{GITLAB_URL}/{team_name}/source/{app_name}",
        jenkins="",  # Jenkins URL을 여기에 입력하십시오.
        argocd="",  # ArgoCD URL을 여기에 입력하십시오.
        kibana="",  # Kibana URL을 여기에 입력하십시오.
        grafana="",  # Grafana URL을 여기에 입력하십시오.
        app_id=app_id
    )
    db.session.add(new_app_url)
    db.session.commit()
    return