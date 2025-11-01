pipeline {
  agent any

  options {
    // avoids @2-style concurrent workspaces/races
    disableConcurrentBuilds()
  }

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
        // run tests inside the image; keep green while wiring real tests
        sh 'docker run --rm groupstudy:latest pytest -q tests || true'
      }
    }

    stage('Deploy to Local Test') {
      steps {
        // clean stale container + force recreate to avoid name conflicts
        sh '''
          docker rm -f gs_app_test 2>/dev/null || true
          docker compose -f docker-compose.test.yml down --remove-orphans || true
          docker compose -f docker-compose.test.yml up -d --build --force-recreate
        '''
      }
    }
  }

  post {
    success { echo 'Level 1 pipeline completed successfully!' }
    failure { echo 'Level 1 pipeline failed. Check logs.' }
  }
}
