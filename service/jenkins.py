import os
import requests

headers = {"Content-Type": "application/x-www-form-urlencoded"}
auth = ("root", "11fc0a375f9ed442743b505c89f984e8a5")
jenkins_url = "http://1.220.201.109:32344"

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