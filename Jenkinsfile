pipeline {
  agent any
environment {
    REGISTRY         = 'docker.io/dockeraccount098'  // your Docker Hub username
    IMAGE_NAME       = 'user-service'
    APP_VERSION      = "${env.BUILD_NUMBER}"
    INFRA_REPO_SSH   = 'git@github.com:eya12378/infra.git'
    K8S_ENV          = 'dev'
    TRIVY_EXIT_CODE  = '1'
    GIT_SSH_CREDS_ID = 'infra-ssh'        // Jenkins SSH key for GitHub
    DOCKER_USER      = 'dockeraccount098' // hardcoded Docker username
    DOCKER_PASSWORD  = 'dockerdocker'     // hardcoded Docker password
    SLACK_WEBHOOK    = 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL' // optional hardcoded
}

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }
    stage('Unit Tests') {
      steps { sh 'pytest -q' }
    }
    stage('Build Image') {
      steps { sh "docker build -t $REGISTRY/$IMAGE_NAME:$APP_VERSION ." }
    }
    stage('Trivy Scan') {
      steps {
        sh """
          trivy image --exit-code ${TRIVY_EXIT_CODE} --severity HIGH,CRITICAL $REGISTRY/$IMAGE_NAME:$APP_VERSION || {
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
          sshagent(['your-ssh-credential-id']) {
            sh """
              rm -rf infra && git clone $INFRA_REPO_SSH
              cd infra/apps/${K8S_ENV}/user-service
              sed -i 's/tag: .*/tag: ${APP_VERSION}/' values.yaml
              git checkout -b bump-user-${APP_VERSION}
              git add values.yaml
              git commit -m "user-service: bump to ${APP_VERSION}"
              git push -u origin bump-user-${APP_VERSION}
            """
          }
        }
      }

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
}
}
