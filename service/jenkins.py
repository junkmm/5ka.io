import requests

headers = {"Content-Type": "application/x-www-form-urlencoded"}
auth = ("root", "11fc0a375f9ed442743b505c89f984e8a5")

def create_jenkins_user(username, password, email, fullname):
    url = "http://1.220.201.109:32344/securityRealm/createAccountByAdmin"
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

# /api/v1/team POST 요청으로 Team 생성 시 Jenkins Item Role 생성
def create_team_and_call_jenkins_api(team_name):
    # Team 생성이 정상적으로 처리되었다면 Jenkins API 호출
    pattern = ".*_"+team_name
    jenkins_api_url = "http://1.220.201.109:32344/role-strategy/strategy/addRole"
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

"""
"""
def create_folder(name):
    header = {'Content-Type': 'text/xml'}
    read = open(XMLPath.FOLDER.value, 'rb') \
        .read()
    url = f'{Jenkins.URL.value}/createItem?name={name}'

    post = requests.post(url, headers=header, data=read, auth=Jenkins.TOKEN.value)
    return post.text