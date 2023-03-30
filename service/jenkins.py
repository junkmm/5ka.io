import os
import requests
from db import db
from models import AppUrlModel, TeamModel, UserModel, ProjectModel, AppModel
from flask_smorest import abort

headers = {"Content-Type": "application/x-www-form-urlencoded"}
jenkins_url = os.getenv("JENKINS_URL")
jenkins_user = os.getenv("JENKINS_AUTH_ID")
jenkins_token = os.getenv("JENKINS_AUTH_TOKEN")
container_repository = os.getenv("CONTAINER_REPOSITORY_IMAGE_NAME")
auth = (jenkins_user, jenkins_token)

# /api/v1/signup POST 요청으로 User 생성 시 Jenkins의 사용자 생성
def create_jenkins_user(username, password, email, fullname):
    url = f"{jenkins_url}/securityRealm/createAccountByAdmin"
    data = {
        "username": username,
        "password1": password,
        "password2": password,
        "email": email,
        "fullname": fullname
    }
    response = requests.post(url, headers=headers, data=data, auth=auth)
    
    if response.status_code != 200:
        raise Exception("Failed to create Jenkins user")

# /api/v1/signup POST 요청으로 User 생성 시 Jenkins의 사용자에 Role 적용하기
def role_bind_jenkins_user(username, teamname):
    url = f"{jenkins_url}/role-strategy/strategy/assignRole"

    # itemRoles 추가
    data1 = {
        "type": "projectRoles",
        "roleName": teamname,
        "sid": username
    }
    response1 = requests.post(url, data=data1, auth=auth)

    # globalRoles 추가
    data2 = {
        "type": "globalRoles",
        "roleName": "developer",
        "sid": username
    }
    response2 = requests.post(url, data=data2, auth=auth)

# /api/v1/team POST 요청으로 Team 생성 시 Jenkins Item Role 생성
def create_team_and_call_jenkins_api(team_name):
    # Team 생성이 정상적으로 처리되었다면 Jenkins API 호출
    pattern = ".*_"+team_name
    jenkins_api_url = f"{jenkins_url}/role-strategy/strategy/addRole"
    jenkins_api_data = {
        "type": "projectRoles",
        "roleName": team_name,
        "pattern": pattern,
        "permissionIds": "hudson.model.Credentials.Create,hudson.model.Credentials.Delete,hudson.model.Credentials.ManageDomains,hudson.model.Credentials.Update,hudson.model.Credentials.View,hudson.model.Item.Build,hudson.model.Item.Cancel,hudson.model.Item.Configure,hudson.model.Item.Create,hudson.model.Item.Move,hudson.model.Item.Read,hudson.model.Item.Workspace,hudson.model.Run.Update,hudson.scm.Tag",
        "overwrite": "true"
    }
    jenkins_response = requests.post(jenkins_api_url, data=jenkins_api_data, auth=auth)

    if jenkins_response.status_code != 200:
        raise Exception("Failed to create Jenkins team")

# /api/v1/project POST 요청으로 project 생성 시 Jenkins project folder 생성
def jenkins_create_folder(name,team_name):
    # Jenkins API의 URL을 설정합니다.
    create_folder_url = f"{jenkins_url}/createItem?name={name}_{team_name}&mode=com.cloudbees.hudson.plugins.folder.Folder&from=&json={{}}"
    # Folder 생성에 필요한 XML 파일 경로를 설정합니다.
    xml_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resource", "folder_template.xml")
    # XML 파일을 읽어옵니다.
    with open(xml_file_path, "r") as f:
        xml = f.read()
    response = requests.post(create_folder_url, auth=auth, headers={"Content-Type": "application/xml"}, data=xml)
    # 호출 결과를 확인합니다.
    if response.status_code == 200:
        print("Folder created successfully!")
    else:
        print(f"Failed to create folder: {response.text}")

# jenkins pipeline 생성하기
def jenkins_create_application_pipeline(team_name,application_name,gitlab_repository_name,app_id):
    url = f"{jenkins_url}/job/5ka.io_{team_name}/createItem?name={application_name}_{team_name}"
    xml_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resource", "job_template.xml")
    # XML 파일 읽기
    with open(xml_file_path, "r") as xml_file:
        xml_data = xml_file.read().format(
            gitlab_repository_name=f"{gitlab_repository_name}.git"
        )

    # 헤더 설정
    headers = {
        "Content-Type": "application/xml"
    }

    print(auth)
    # Jenkins에 API 요청
    response = requests.post(
        url,
        data=xml_data,
        headers=headers,
        auth=auth
    )
    # 호출 결과를 확인합니다.
    if response.status_code == 200:
        print("Folder created successfully!")
    else:
        print(f"Failed to create folder: {response.text}")

    #http://1.220.201.109:32344/job/5ka.io_dev/job/api-create-test11_dev/
    created_pipeline_url = f"{jenkins_url}/job/5ka.io_{team_name}/job/{application_name}_{team_name}"

    # AppUrlModel에 저장
    app_url_record = AppUrlModel.query.filter(AppUrlModel.app_id == app_id).first()
    app_url_record.jenkins = created_pipeline_url
    db.session.commit()

# Jenkins pipeline 실행시키기
def jenkins_buildwithparameter_pipeline(team_name,app_name):
    app = AppModel.query.filter(AppModel.name == app_name).first()
    user = UserModel.query.filter(UserModel.id == app.user_id).first()
    appurl = AppUrlModel.query.filter(AppUrlModel.app_id == app.id).first()
    data = {
        # user 정보 - 이름, 이메일
        # gitlab url 정보 - source.git helm.git, non-http_helm.git
        # docker hum repository - 고정(로컬 실행 시 docker repository, EKS 실행 시 EKS 주소) -> 환경변수 처리 필요
        'gitlabName': user.user_id,
        'gitlabEmail':user.email,
        'gitlabWebaddress': f"{appurl.gitlab_source}.git",
        'githelmaddress':f"{appurl.gitlab_helm}.git",
        'githelmshortddress':f"{appurl.gitlab_helm.replace('http://','')}.git",
        'gitlabCredential':'git_cre',
        'dockerHubRegistry':container_repository,
        'dockerHubRegistryCredential':'docker_cre',
    }
    url = f"{jenkins_url}/job/5ka.io_{team_name}/job/{app_name}_{team_name}/buildWithParameters"
    response = requests.post(url, auth=auth, data=data)
    if response.status_code != 201:
        abort(400, message="Build Error")
    return {"message":"Build successfully"}, 201