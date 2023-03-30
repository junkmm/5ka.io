pipeline {
  agent any
  // any, none, label, node, docker, dockerfile, kubernetes
  tools {
    maven 'my_maven'
  }
  
  parameters {
    string(name: 'gitlabName', defaultValue: 'root')
    string(name: 'gitlabEmail', defaultValue: 'root@5ka.io')
    string(name: 'gitlabWebaddress', defaultValue: '', description: 'git source repository')
    string(name: 'githelmaddress', defaultValue: '', description: 'git helm repository')
    string(name: 'githelmshortddress', defaultValue: '', description: 'git helm repository')
    string(name: 'gitlabCredential', defaultValue: 'git_cre', description: 'git credentials')
    string(name: 'dockerHubRegistry', defaultValue: 'kimhj4270/5kaspring', description: 'docker registry')
    string(name: 'dockerHubRegistryCredential', defaultValue: 'docker_cre', description: 'docker credential 생성시의 ID')
  }

    stages {
    stage('Checkout Gitlab') {
      steps {
        checkout([$class: 'GitSCM', branches: [[name: '*/master']], extensions: [], userRemoteConfigs: [[credentialsId:  "${params.gitlabCredential}", url: "${params.gitlabWebaddress}"]]])
      }
      post {
        failure {
          echo 'Repository clone failure'
        }
        success {
          echo 'Repository clone success'
        }
      }
    }
    stage('Maven Build') {
      steps {
        sh 'mvn clean install'
        // maven 플러그인이 미리 설치 되어있어야 함.
      }
      post {
        failure {
          echo 'maven build failure'
        }
        success {
          echo 'maven build success'
        }
      }
    }
    stage('Docker image Build & tag') {
      steps {
       
        sh "docker build -t ${params.dockerHubRegistry}:${currentBuild.number} ."
        // kyontoki/SPimage 이런식으로 빌드가 될것이다.
        // currentBuild.number 젠킨스에서 제공하는 빌드넘버변수.
      }
      post {
        failure {
          echo 'docker image build failure'
        }
        success {
          echo 'docker image build success'
        }
      }
    }
    stage('docker image push') {
      steps {
        withDockerRegistry(credentialsId: "${params.dockerHubRegistryCredential}", url: '') {
          // withDockerRegistry : docker pipeline 플러그인 설치시 사용가능.
          // dockerHubRegistryCredential : environment에서 선언한 docker_cre  
            sh "docker push ${params.dockerHubRegistry}:${currentBuild.number}"
        }
      }
      post {
        failure {
          echo 'docker image push failure'
          sh "docker image rm -f ${params.dockerHubRegistrsy}:${currentBuild.number}"
          sh "docker image rm -f ${params.dockerHubRegistry}:latest"
        }
        success {
          sh "docker image rm -f ${params.dockerHubRegistry}:${currentBuild.number}"
          sh "docker image rm -f ${params.dockerHubRegistry}:latest"  
          echo 'docker image push success'
        }
      }
    }

     stage('5ka Manifest Repository change') {
        steps {
            git credentialsId: "${params.gitlabCredential}",
                url: "${params.githelmaddress}",
                branch: 'main'
        }
        post {
                failure {
                  echo '5ka Repository change failure !'
                }
                success {
                  echo '5ka Repository change success !'
                }
        }
    }

    stage('K8S Manifest Update') {
        steps {
            withCredentials([usernamePassword(credentialsId: "${params.gitlabCredential}", passwordVariable: 'password', usernameVariable: 'username')]) {
              sh "echo 'hihi' >> README.md"
              sh "git init"
              sh "git add ."
              sh "git config --global user.email ${params.gitlabName}"
              sh "git config --global user.name ${params.gitlabEmail}"
              sh "git commit -m '[UPDATE] 5ka ${currentBuild.number} image versioning'"
              sh "git remote set-url origin http://${username}:${password}@${githelmshortddress}"
              sh "git push origin main"
            }
        }
        post {
                failure {
                  echo 'K8S Manifest Update failure !'
                }
                success {
                  echo 'K8S Manifest Update success !'
                }
        }
    }
  }
}
