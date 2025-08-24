pipeline {
    agent any
    environment {
        REGISTRY = 'docker.io/dockeraccount098'
        IMAGE_NAME = 'user-service'
        APP_VERSION = "${env.BUILD_NUMBER}"
        INFRA_REPO_SSH = 'git@github.com:eya12378/infra.git'
        K8S_ENV = 'dev'
        DOCKER_USER = 'dockeraccount098'
        DOCKER_PASSWORD = 'dockerdocker'
        SLACK_WEBHOOK = 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
    }

    stages {
        stage('Checkout') { steps { checkout scm } }
        stage('Unit Tests') { steps { sh 'pytest -q' } }
        stage('Build Image') { steps { sh "docker build -t $REGISTRY/$IMAGE_NAME:$APP_VERSION ." } }
        stage('Trivy Scan') {
            steps {
                sh """
                  trivy image --exit-code 1 --severity HIGH,CRITICAL $REGISTRY/$IMAGE_NAME:$APP_VERSION || {
                    echo 'Image scan failed'; exit 1;
                  }
                """
            }
        }
        stage('Push Image') {
            steps {
                sh """
                  echo $DOCKER_PASSWORD | docker login -u $DOCKER_USER --password-stdin
                  docker push $REGISTRY/$IMAGE_NAME:$APP_VERSION
                """
            }
        }
        stage('Create Infra PR (bump tag)') {
            steps {
                withCredentials([string(credentialsId: 'github-token-id', variable: 'GITHUB_TOKEN')]) {
                    sh '''
                        rm -rf infra
                        git clone https://$GITHUB_TOKEN@github.com/eya12378/infra.git
                        cd infra/apps/dev/user-service
                        sed -i s/tag:.*/tag:12/ values.yaml
                        git checkout -b bump-user-12
        
                        # Set Git user identity
                        git config user.name "eya12378"
                        git config user.email "eya.touili@eniso.u-sousse.tn"
        
                        git add values.yaml
                        git commit -m "user-service: bump to 12"
                        git push origin bump-user-12
                    '''
                }
            }
        }

    } // end of stages

    post {
        success {
            sh """curl -X POST -H 'Content-type: application/json' \
              --data '{"text":"✅ Deployed *user-service* version *${APP_VERSION}* to *${K8S_ENV}* (awaiting ArgoCD sync)"}' \
              $SLACK_WEBHOOK"""
        }
        failure {
            sh """curl -X POST -H 'Content-type: application/json' \
              --data '{"text":"❌ Build failed for *user-service*"}' \
              $SLACK_WEBHOOK"""
        }
    }
} // end of pipeline
