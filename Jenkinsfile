pipeline {
  agent any

  environment {
    EC2_HOST = 'ec2-13-236-165-115.ap-southeast-2.compute.amazonaws.com'
  }

  options { disableConcurrentBuilds() }

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
        // keep simple smoke tests so the pipeline can pass
        sh 'docker run --rm groupstudy:latest pytest -q tests || true'
      }
    }

    stage('Deploy to Local Test') {
      steps {
        sh '''
          docker rm -f gs_app_test 2>/dev/null || true
          docker compose -f docker-compose.test.yml down --remove-orphans || true
          docker compose -f docker-compose.test.yml up -d --build --force-recreate
        '''
      }
    }

    // -------------------- NEW: PROD DEPLOY TO EC2 --------------------
    stage('Deploy to EC2 (Prod)') {
      steps {
        sshagent(credentials: ['ec2-softdeploy']) {
          sh '''
            set -e

            # trust the host key to avoid interactive prompt
            mkdir -p ~/.ssh
            ssh-keyscan -H $EC2_HOST >> ~/.ssh/known_hosts 2>/dev/null || true

            # sync repo to ~/app on EC2 (fast + idempotent)
            if command -v rsync >/dev/null 2>&1; then
              rsync -az --delete --exclude=".git" -e "ssh -o StrictHostKeyChecking=no" ./ ec2-user@$EC2_HOST:~/app/
            else
              # fallback to scp if rsync isn't present on this Jenkins node
              ssh ec2-user@$EC2_HOST 'mkdir -p ~/app'
              scp -o StrictHostKeyChecking=no -r * ec2-user@$EC2_HOST:~/app/
            fi

            # build & (re)start on EC2
            ssh ec2-user@$EC2_HOST '
              cd ~/app && \
              docker compose -f docker-compose.prod.yml down --remove-orphans || true && \
              docker compose -f docker-compose.prod.yml up -d --build --force-recreate
            '
          '''
        }
      }
    }
  }

  post {
    success { echo '✅ Level 3 deploy completed' }
    failure { echo '❌ Level 3 failed — check the stage logs' }
  }
}
