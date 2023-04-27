# Backend 정리

## 환경변수

- .flaskenv
    
    ```bash
    FLASK_APP=app
    FLASK_DEBUG=1
    
    DEV_CLUSTER_NAME=arn:aws:eks:ap-northeast-2:963897741994:cluster/eks-ks5-app-dev
    OPS_CLUSTER_NAME=arn:aws:eks:ap-northeast-2:963897741994:cluster/eks-ks5-app-dev
    
    DB_URL_LOCAL=mysql+pymysql://root:1234@127.0.0.1:3306/5ka_jun
    DB_URL=mysql+pymysql://dbuser:1234@1.220.201.109:33306/5ka_jun
    
    JENKINS_HEADERS={"Content-Type": "application/x-www-form-urlencoded"}
    JENKINS_AUTH_ID=root
    JENKINS_AUTH_TOKEN=11e0aaa8681f96be4407a8c8a7a5457c13
    JENKINS_URL=http://jenkins-service.jenkins.cluster.local:8080
    CONTAINER_REPOSITORY_IMAGE_NAME=kimhj4270/5kaspring
    
    GITLAB_URL=http://gitlab-service.gitlab.cluster.local
    GITLAB_TOKEN=glpat-N6iD__WvaKWA82J5iiNJ
    
    ARGO_URL=https://argocd-server.argocd.cluster.local
    ARGO_TOKEN=Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhcmdvY2QiLCJzdWIiOiJhcGl1c2VyOmFwaUtleSIsIm5iZiI6MTY4MDc2ODMxOCwiaWF0IjoxNjgwNzY4MzE4LCJqdGkiOiJhZTEzZjc1Mi1iMzNiLTRhNTctYjgyNS02MWQ1YzJiZjY2MTQifQ.AwuopI58lWcudN2kqu8j8BtBVN_p_Mj1J08NWZFcw7s
    
    KIBANA_URL=http://elasticsearch-svc-lb.kube-logging.cluster.local:9200
    KIBANA_USER=elastic
    KIBANA_PWD=test123
    
    JENKINS_EXT_URL=https://jenkins.ihp001.dev
    GITLAB_EXT_URL=https://gitlab.ihp001.dev
    ARGO_EXT_URL=https://argocd.ihp001.dev
    KIBANA_EXT_URL=https://kibanadashboard.ihp001.dev
    ```
    

## Workflow

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/3816d4cf-ce98-4290-80af-c8481143a0a3/Untitled.png)

## db Diagram

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/7e8456e8-deff-4f62-ad37-0ccb6535a709/Untitled.png)

## API 기능 설명

## 유저 가입 & 로그인

## 기능 요약

웹 콘솔에서 회원가입 시 Gitlab, Jenkins, Kibana의 User를 생성합니다. 해당 User로 각 각의 오픈소스로 접근할 수 있습니다.

## API

### /api/v1/signup - POST

<aside>
💡 Front로 부터 회원 정보를 전달받아 회원가입을 진행하는 API 입니다.

</aside>

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/e4757b1b-bf13-49d7-9275-32b4da3519fa/Untitled.png)

| 구분 | 설명 |
| --- | --- |
| 회원 정보 전달 | Front로부터 회원 정보를 전달 받습니다. |
| 중복검사(id, email) | 전달받은 데이터와 데이터베이스 users table의 id, email과 중복 검사를 진행합니다. |
| 회원 정보 DB 저장 | 중복검사 통과 시 users table에 회원 정보를 입력합니다. |
| 각 컴포넌트 유저 생성 | 각 컴포넌트의 user 생성 api를 호출합니다. |
| Jenkins | 미리 정의한 Role에 User를 Assign 합니다.
dev팀의 사용자는 _dev 이름으로 끝나는 작업만 접근 가능합니다.
* 사용 API
  회원가입(POST) - /securityRealm/createAccountByAdmin
  Role 연결(POST) - /role-stratrgy/strategy/assignRole |
| Gitlab | 미리 정의한 Group에 User를 Join 합니다.
dev팀의 사용자는 dev 그룹 하위의 project에만 접근 가능합니다.
* 사용 API
  회원가입(POST) - /api/v4/users
  그룹 정보 조회(GET) - /api/v4/groups/{group-name}
  사용자 그룹 가입(POST) - /api/v4/groups/{group-id}/members |
| Kibana | 미리 정의한 Role에 User를 Assign 합니다.
dev팀의 사용자는 dev 클러스터의 dashboard에만 접근 가능합니다.
* 사용 API
  회원가입(POST) - /_security/user/{user-id}?pretty |

### /api/v1/Login - POST

<aside>
💡 Front로 부터 로그인 정보를 받고 데이터베이스 정보와 비교 검증합니다. 성공 시 Front에 201코드를 반환하며 Front는 쿠키를 생성합니다.

</aside>

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/cfaca294-58a3-4f2d-ac8e-0035987fd48b/Untitled.png)

| 구분 | 설명 |
| --- | --- |
| 로그인 정보 전달 | Front로부터 로그인 정보를 전달 받습니다. |
| 검증 | 전달받은 데이터와 데이터베이스 users table의 id, password를 비교합니다.
 - 불일치 시 401 에러 코드와 Invalid credentials 메시지를 반환합니다. |
| 로그인 성공 | 검증 결과 로그인 성공 시 201 코드를 반환합니다. |

## 프로젝트 관련

## 기능 요약

Gitlab, Jenkins, Argocd 등 최소단위 Application의 그룹화를 위해 Project를 생성합니다. 1개의 프로젝트에는 여러개의 Application이 생성 됩니다. 아래 표는 컴포넌트 별 Application 매칭을 보여줍니다.

| 구분 | GitLab | Jenkins | Argocd | Kubernetes | Grafana | Kibana |
| --- | --- | --- | --- | --- | --- | --- |
| Team | Group | Folder | - | Cluster | - | Cluster |
| Project | - | - | - | - | - | - |
| Application | Repository | Pipeline | Application | Namespace | - | - |

## API

### /api/v1/project - POST

<aside>
💡 Front로 부터 프로젝트 정보를 전달받아 데이터베이스에 프로젝트를 생성합니다.

</aside>

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/5ae215eb-e5ac-4224-b651-1bccfb8441c1/Untitled.png)

| 구분 | 설명 |
| --- | --- |
| 프로젝트 정보 전달 | Front로부터 프로젝트 정보를 전달 받습니다. |
| 중복검사(name) | 전달받은 데이터와 데이터베이스 projects table의 name과 중복 검사를 진행합니다. |
| 프로젝트 정보 DB 저장 | 중복검사 통과 시 projects table에 프로젝트 정보를 입력합니다. |

### /api/v1/project/{team-id} - GET

<aside>
💡 projects 테이블의 team-id에 해당하는 정보를 반환합니다. 따라서 dev 사용자 로그인 시 dev팀에서 생성된 프로젝트 정보를 Front에서 확인할 수 있습니다.

</aside>

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/dfc7afbf-96b9-4adb-8253-a851a4abfa67/Untitled.png)

| 구분 | 설명 |
| --- | --- |
| 프로젝트 정보 요청 | Front로부터 프로젝트 정보 요청을 전달받습니다. |
| 정보 조회 | 요청받은 정보중 team-id에 해당하는 정보를 projects 테이블의 team-id를 기준으로 데이터를 조회합니다. |
| 반환 | 조회한 데이터를 json 형태로 반환합니다. |

## 애플리케이션 관련

## 기능 요약

생성한 Project에서 Application을 생성합니다. Application 생성 시 이름, Type, 설명을 입력 받습니다. 이 때 Type은 Spring, Django, Flask 3가지 종류로 설정되어 있으며 만약 Spring Type의 Application 생성 시 아래 흐름으로 Application을 생성합니다.

## API

### /api/v1/app- POST

<aside>
💡 Front로 부터 application생성 요청을 전달받아 application을 생성합니다. application 생성 대상은 gitlab의 source, helm repository, jenkins의 pipeline, argocd의 application이며 상호간 설정(레포지토리 주소 등)을 자동화 하여 CI/CD 파이프라인이 작동 되도록 합니다.

</aside>

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/421da3f6-b32e-46df-9745-79fb0481b819/Untitled.png)

| 구분 | 설명 |
| --- | --- |
| Application 정보 전달 | Front로 부터 Application 생성 정보를 전달 받습니다. |
| 검증 | 전달받은 데이터와 데이터베이스 apps table의 name과 비교하여 이름 중복검사를 진행합니다. |
| Application 정보 DB 저장 | 중복검사 통과 시 apps table에  Application 정보를 입력합니다. |
| 각 컴포넌트 Application 생성 | 전달받은 데이터를 기준으로 각 컴포넌트에 Application을 생성하여 CI/CD 환경을 자동 구성 합니다. |
| Gitlab | 아래와 같은 Step으로 Gitlab의 Repository를 생성합니다.
1. 입력받은 Type을 기준으로 Template Repository id를 검색합니다.
2. 검색된 id로 입력받은 Application name의 repository로 fork 합니다.
3. Helm Repository를 Application name_helm으로 fork 합니다.
4. fork된 Repository id조회 후 Developer 접근 권한을 부여합니다.
5. user가 dev팀 소속인 경우 dev 그룹의 하위로 생성합니다.
* 사용 API
  Repository id 조회(GET) - /api/v4/projects?search={type}_Template
  Repository fork(POST) - /api/v4/projects/{Template_id}/fork
  Repository 권한 부여(PATCH) - /api/v4/projects/{Forked_repo_id}/protected_branchs/{branch_name} |
| Jenkins | 아래와 같은 Step으로 Jenksins의 Pipeline을 생성합니다.
1. Jenkins Pipeline을 생성하는 xml Template을 준비합니다.
2. xml값 중 repository 값을 Gitlab repository주소로 변경합니다.
3. 변경된 xml값을 기반으로 Pipeline 생성 API를 호출합니다.
4. Gitlab Source Repository와 연결된 Pipeline이 생성됩니다.
* 사용 API
  Pipeline 생성(POST) - /job/{team-folder}/createItem?name={application_name}_{team_name} |
| Argocd | Argocd의 Application 생성 시 Repository주소가 반드시 필요합니다. 따라서 Gitlab Helm Repository 생성 API를 호출한 직후 최대 30초 동안 repository 상태를 확인하고, 정상 확인 시 Application을 생성합니다.

아래와 같은 Step으로 Argocd의 Application을 생성합니다.
1. Argocd Application을 생성하는 Json Template을 준비합니다.
2. Json 값 중 이름, 배포 클러스터, git 주소, Helm param을 변경합니다.
3. Argocd Setting에 Repository 주소를 허가합니다.
4. 변경된 Json을 기반으로 Application 생성 API를 호출합니다.
5. Gitlab Helm Repository와 연결된 Application이 생성됩니다.
* 사용 API
  Repository 등록(POST) - /api/v1/repositories
  Application 생성(POST) - /api/v1/applications |

### /api/v1/apps/{project-id} - GET

<aside>
💡 apps 테이블의 project-id에 해당하는 정보를 반환합니다. 따라서 project 내 Application 정보를 Front에서 확인할 수 있습니다.

</aside>

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/acb2bae2-724a-4542-bd20-88a7cc751bbf/Untitled.png)

| 구분 | 설명 |
| --- | --- |
| 애플리케이션 정보 요청 | Front로부터 애플리케이션 정보 요청을 전달받습니다. |
| 정보 조회 | 요청받은 정보중 project-id에 해당하는 정보를 apps 테이블의 project-id를 기준으로 데이터를 조회합니다. |
| 반환 | 조회한 데이터를 json 형태로 반환합니다. |

## 앱 빌드

## 기능 요약

생성한 Application의 Jenkins pipeline 빌드 요청을 보내는 API입니다. 사용자는 Gitlab Source Repository에 코드를 Push해 둔 상태에서 Build 버튼을 클릭합니다. Backend에서는 Jenkins의 BuildwithParameter API를 호출해 Jenkins 빌드를 진행합니다.

## API

### /api/v1/jenkins/{app_id}- GET

<aside>
💡 {app_id}에 해당하는 Application의 Jenkins를 BuildwithParameter 방식으로 빌드 합니다.

</aside>

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/5a3b00a8-1a4c-4c8f-81e5-ffd0dc139e02/Untitled.png)

| 구분 | 설명 |
| --- | --- |
| Jenkins 빌드 요청 | Front로 부터 Jenkins 빌드 요청을 받습니다. 이 때 app_id 값도 함께 받습니다. |
| 검증 | 전달받은 데이터와 데이터베이스 apps table의 id과 비교하여 존재 유무를 확인합니다. |
| Jenkins Build | 아래와 같은 step으로 Jenkins Build를 진행합니다.
1. app_id에 해당하는 Application의 Jenkins Pipeline 정보 가져오기
2. BuildwithParameter로 호출 할 데이터 준비
  - gitlab_address
  - gitlab_helm_address
  - gitlab_credential
  - namespace(app_name)
  - ETC
3. BuildwithParamater API 호출을 통해 Jenkins Build를 진행합니다.
* 사용 API
  Build 요청(POST) - /job/{folder}/job/{appname}/buildWithParameters |

## 앱 배포
