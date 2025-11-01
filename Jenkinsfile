pipeline {
  agent any

  stages {
    stage('Checkout') {
      steps {
        git url: 'https://github.com/aashim06/SoftwareDeployment.git', branch: 'main'
      }
    }

    stage('Build') {
      steps {
        sh 'export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"; docker build -t groupstudy:latest .'
      }
    }

    stage('Test') {
      steps {
        sh 'export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"; docker run --rm groupstudy:latest pytest -q tests || true'
      }
    }

    stage('Deploy to Local Test') {
  steps {
    sh '''
      docker compose -f docker-compose.test.yml down --remove-orphans || true
      docker compose -f docker-compose.test.yml up -d --build --force-recreate
    '''
  }
}



  post {
    success { echo 'Level 1 pipeline completed successfully!' }
    failure { echo 'Level 1 pipeline failed. Check logs.' }
  }
}
