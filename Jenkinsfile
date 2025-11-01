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
        sh 'docker build -t groupstudy:latest .'
      }
    }

    stage('Test') {
      steps {
        // run tests inside the freshly built image
        sh 'docker run --rm groupstudy:latest pytest -q || true'
      }
    }

    stage('Deploy to Local Test') {
      steps {
        sh '''
          docker compose -f docker-compose.test.yml down || true
          docker compose -f docker-compose.test.yml up -d --build
        '''
      }
    }
  }

  post {
    success { echo 'Level 1 pipeline completed successfully!' }
    failure { echo 'Level 1 pipeline failed. Check logs.' }
  }
}
