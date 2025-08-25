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

        stage('Build Image') {
            steps {
                sh "docker build -t $REGISTRY/$IMAGE_NAME:$APP_VERSION ."
            }
        }

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
                        set -e
                        BRANCH_NAME="bump-user-${APP_VERSION}"
                        REPO_DIR="infra"
                        APP_PATH="apps/dev/user-service"

                        rm -rf $REPO_DIR
                        git clone https://$GITHUB_TOKEN@github.com/eya12378/infra.git $REPO_DIR
                        cd $REPO_DIR

                        if git ls-remote --heads origin $BRANCH_NAME | grep $BRANCH_NAME; then
                            git checkout $BRANCH_NAME
                            git reset --hard origin/$BRANCH_NAME
                        else
                            git checkout -b $BRANCH_NAME
                        fi

                        sed -i "s/tag:.*/tag:${APP_VERSION}/" $APP_PATH/values.yaml

                        git config user.name "eya12378"
                        git config user.email "eya.touili@eniso.u-sousse.tn"

                        git add $APP_PATH/values.yaml
                        git commit -m "user-service: bump to ${APP_VERSION}" || echo "No changes to commit"
                        git push origin $BRANCH_NAME
                    '''
                }
            }
        }

        stage('Start Monitoring Stack') {
            steps {
                dir('user_service') {
                    sh 'docker-compose up -d --build'
                }
            }
        }

        stage('Expose ArgoCD') {
            steps {
                sh '''
                  echo "🔄 Restarting ArgoCD port-forward on 8083..."
                  # Kill any old port-forward processes
                  pkill -f "kubectl port-forward.*argocd-server" || true

                  # Run port-forward in background
                  nohup kubectl port-forward --address 0.0.0.0 svc/argocd-server -n argocd 8083:443 > argocd-portforward.log 2>&1 &
                  sleep 3
                  echo "✅ ArgoCD available at https://$(curl -s ifconfig.me):8083"
                '''
            }
        }
    }

        post {
            success {
                sh """curl -X POST -H 'Content-type: application/json' \
                  --data '{"text":"✅ Deployed *\${APP_VERSION}* to *\${K8S_ENV}* (ArgoCD: https://$(curl -s ifconfig.me):8083 , Grafana/Prometheus via docker-compose)"}' \
                  $SLACK_WEBHOOK"""
            }
            failure {
                sh """curl -X POST -H 'Content-type: application/json' \
                  --data '{"text":"❌ Build failed for *\${APP_VERSION}*"}' \
                  $SLACK_WEBHOOK"""
            }
        }

}
