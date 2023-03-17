import requests
import json

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
    data = {'user_id': user_id, 'access_level': 20}
    response = requests.post(f'{GITLAB_URL}/api/v4/groups/{group_id}/members', headers=headers, json=data)

    if response.status_code == 201:
        print('User added to group successfully!')
    else:
        print('Failed to add user to group.')