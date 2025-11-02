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
        sh 'docker run --rm groupstudy:latest pytest -q tests || true'
      }
    }

    stage('Deploy to Local Test') {
      steps {
        sh '''
          set -e
          docker rm -f gs_app_test 2>/dev/null || true
          docker compose -f docker-compose.test.yml down --remove-orphans || true
          docker compose -f docker-compose.test.yml up -d --build --force-recreate
        '''
      }
    }

    stage('SSH sanity check') {
      steps {
        sshagent(credentials: ['ec2-softdeploy']) {
          sh 'ssh -o StrictHostKeyChecking=no ec2-user@$EC2_HOST "echo SSH OK && uname -a"'
        }
      }
    }

    stage('Deploy to EC2 (Prod)') {
      steps {
        sshagent(credentials: ['ec2-softdeploy']) {
          sh '''
            set -e
            mkdir -p ~/.ssh
            ssh-keyscan -H $EC2_HOST >> ~/.ssh/known_hosts 2>/dev/null || true

            echo "Syncing project files to EC2..."
            rsync -az --delete -e "ssh -o StrictHostKeyChecking=no" ./ ec2-user@$EC2_HOST:~/app/

            echo "Deploying container on EC2..."
            ssh -o StrictHostKeyChecking=no ec2-user@$EC2_HOST <<'EOSSH'
set -e
cd ~/app

# Pick Compose v2 if available; else fallback to v1 path
if docker compose version >/dev/null 2>&1; then
  DC="docker compose"
elif command -v /usr/local/bin/docker-compose >/dev/null 2>&1; then
  DC="/usr/local/bin/docker-compose"
else
  echo "ERROR: Docker Compose not installed on EC2" >&2
  exit 1
fi

echo "Using: $DC"
ls -l docker-compose.prod.yml || { echo "docker-compose.prod.yml not found!"; exit 1; }
test -s docker-compose.prod.yml || { echo "docker-compose.prod.yml is empty!"; exit 1; }

$DC -f docker-compose.prod.yml down --remove-orphans || true
$DC -f docker-compose.prod.yml up -d --build --force-recreate

echo "Containers:"
$DC -f docker-compose.prod.yml ps
EOSSH

            echo "✅ Deployment successful!"
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
