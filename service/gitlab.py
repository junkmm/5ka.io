import time
import requests
import json
from models.apps_url import AppUrlModel
from db import db
from models.teams import TeamModel
import os
from service.argocd import create_argocd_application

GITLAB_EXT_URL = os.getenv("GITLAB_EXT_URL")
KIBANA_EXT_URL = os.getenv("KIBANA_EXT_URL")
GITLAB_URL = os.getenv("GITLAB_URL")
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")

def gitlab_create_user_and_join_group(name, email, password, group_name):
    print(name,email,password,group_name)
    headers = {"Content-Type": "application/json", "PRIVATE-TOKEN": GITLAB_TOKEN}

    # GitLab 사용자 생성하기
    data = {'name': name, 'username': name, 'email': email, 'password': password, "skip_confirmation": True}
    response = requests.post(f'{GITLAB_URL}/api/v4/users', headers=headers, json=data, verify=False)

    if response.status_code != 201:
        print('Failed to create user.')
        print(f"User creation failed with status code: {response.status_code}, and content: {response.content}")
        return

    # team의 source subgroup GID 조회하기
    user_id = response.json()['id']
    response = requests.get(f'{GITLAB_URL}/api/v4/groups/{group_name}', headers=headers, verify=False)

    if response.status_code != 200:
        print(f"Failed to retrieve group {group_name} information.")
        return

    try:
        group_id = response.json()['id']
    except IndexError:
        print(f"Group with name {group_name} does not exist.")
        return

    # 사용자 그룹에 추가하기
    data = {'user_id': user_id, 'access_level': 30}
    response = requests.post(f'{GITLAB_URL}/api/v4/groups/{group_id}/members', headers=headers, json=data, verify=False)

    if response.status_code == 201:
        print('User added to group successfully!')
    else:
        print('Failed to add user to group.',response.url)

def gitlab_create_application_from_fork(type,app_name,team_id,app_id):
    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
    # team_id로 team명 추출하기
    team = TeamModel.query.filter(TeamModel.id == team_id).first()
    team_name = team.name

    # source, helm url 저장
    new_app_url = AppUrlModel(
        gitlab_source=f"{GITLAB_EXT_URL}/{team_name}/source/{app_name}",
        gitlab_helm=f"{GITLAB_EXT_URL}/{team_name}/helm/{app_name}",
        jenkins="",  # Jenkins URL을 여기에 입력하십시오.
        argocd="",  # ArgoCD URL을 여기에 입력하십시오.
        kibana="https://kibanadashboard.ihp001.dev/app/discover#/?_g=()&_a=(columns:!(_source),filters:!(),index:e1321040-d8dd-11ed-86ed-1962963f7307,interval:auto,query:(language:kuery,query:''),sort:!())",  # Kibana URL을 여기에 입력하십시오.
        grafana="",  # Grafana URL을 여기에 입력하십시오.
        app_id=app_id
    )
    db.session.add(new_app_url)
    db.session.commit()

    project_access_data = {
        "allowed_to_push": {"access_levels": [{"access_level": 30}]},
        "allowed_force_push": {"access_levels": [{"access_level": 30}]}
    }
    # GitLab "Spring Template" 프로젝트 조회하여 ID 획득
    # spring이면 template 이름이 Sprint_Template 여야 함.
    source_url = f"{GITLAB_URL}/api/v4/projects?search={type}_Template"
    response = requests.get(source_url, headers=headers, verify=False)
    source_project_id = response.json()[0]['id']

    # Helm Template ID 획득
    helm_url = f"{GITLAB_URL}/api/v4/projects?search=Helm_Template"
    response = requests.get(helm_url, headers=headers, verify=False)
    helm_project_id = response.json()[0]['id']

    # Source Fork 요청 보내기
    url = f"{GITLAB_URL}/api/v4/projects/{source_project_id}/fork"
    data = {"namespace_path": team_name+"/source", "name": app_name, "path": app_name, "visibility": "public"}
    response = requests.post(url, headers=headers, data=data, verify=False)
    # Source Forked Project의 branch 권한 수정 - 이거 해야 그룹 사용자가 push 가능
    forked_source_project_id = response.json().get('id')
    default_branch = response.json().get('default_brancd')
    response = requests.patch(f"{GITLAB_URL}/api/v4/projects/{forked_source_project_id}/protected_branches/{default_branch}", headers=headers, json=project_access_data, verify=False)

    # Helm Fork 요청 보내기
    helm_url = f"{GITLAB_URL}/api/v4/projects/{helm_project_id}/fork"
    helm_data = {"namespace_path": team_name+"/helm", "name": app_name, "path": app_name, "visibility": "public"}
    response = requests.post(helm_url, headers=headers, data=helm_data, verify=False)
    # Helm Forked Project의 branch 권한 수정 - 이거 해야 그룹 사용자가 push 가능
    forked_helm_project_id = response.json().get('id')
    default_branch = response.json().get('default_brancd')
    response = requests.patch(f"{GITLAB_URL}/api/v4/projects/{forked_helm_project_id}/protected_branches/{default_branch}", headers=headers, json=project_access_data, verify=False)

    # forked helm repository가 준비 됐는지 확인하고, 준비 되면 argo app 올리기
    # Job ID로 상태 조회하기
    import_status = 'created'
    while import_status != 'finished':
        response = requests.get(f'{GITLAB_URL}/api/v4/projects/{forked_helm_project_id}', headers=headers, verify=False)
        if response.status_code != 200:
            print('Failed to get job status')
            return
        import_status = response.json().get('import_status')
        if import_status == 'finished':
            # repository URL이 이 시점에서 생성되어 반환됩니다.
            create_argocd_application(app_name, type, team_name, app_id)
        else:
            # 5초마다 상태를 확인합니다.
            time.sleep(0.5)