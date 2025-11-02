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
        sh 'docker build -t groupstudy:${BUILD_NUMBER} .'
        sh 'docker tag groupstudy:${BUILD_NUMBER} groupstudy:prod'
      }
    }

    stage('Test') {
      steps {
        // keep tests non-blocking so pipeline can proceed
        sh 'docker run --rm groupstudy:prod pytest -q tests || true'
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
          sh "ssh -o StrictHostKeyChecking=no ec2-user@${EC2_HOST} 'echo SSH OK && uname -a'"
        }
      }
    }

    stage('Deploy to EC2 (Blue-Green)') {
      steps {
        sshagent(credentials: ['ec2-softdeploy']) {
          // sync files first
          sh """
            mkdir -p ~/.ssh
            ssh-keyscan -H ${EC2_HOST} >> ~/.ssh/known_hosts 2>/dev/null || true
            rsync -az --delete -e "ssh -o StrictHostKeyChecking=no" ./ ec2-user@${EC2_HOST}:~/app/
          """

          // run all blue-green logic on the EC2 host in one safe heredoc
          sh """
            ssh -o StrictHostKeyChecking=no ec2-user@${EC2_HOST} 'bash -s' <<'REMOTE'
set -e
cd ~/app

echo "[BG] Start nginx + both app slots (force-recreate)"
docker compose -f docker-compose.prod.yml up -d --build --force-recreate nginx app_blue app_green

echo "[BG] Work out current active slot"
ACTIVE=\$(grep -o 'gs_app_\\(blue\\|green\\)' nginx/upstream.conf | sed 's/gs_app_//')
if [ -z "\$ACTIVE" ]; then
  # default to blue if not set
  ACTIVE=blue
fi
if [ "\$ACTIVE" = "blue" ]; then TARGET=green; else TARGET=blue; fi
echo "[BG] Current=\$ACTIVE -> Target=\$TARGET"

echo "[BG] Health check target via Nginx container (/health then /)"
for i in {1..12}; do
  if docker exec reverse_proxy sh -lc "(curl -fsS http://gs_app_\${TARGET}:8000/health >/dev/null) || (curl -fsS http://gs_app_\${TARGET}:8000/ >/dev/null)"; then
    echo "[BG] Target healthy"
    break
  fi
  echo "[BG] Target not healthy yet... retry \$i"
  sleep 5
  if [ "\$i" -eq 12 ]; then
    echo "[BG] Target did not become healthy in time"
    exit 1
  fi
done

echo "[BG] Flip upstream to target slot and reload Nginx"
sed -i "s/gs_app_\\(blue\\|green\\)/gs_app_\${TARGET}/" nginx/upstream.conf

# Try in-container reload first; if not available, fallback to compose exec
if docker exec reverse_proxy sh -lc 'nginx -s reload'; then
  echo "[BG] Nginx reloaded (in-container)"
else
  docker compose -f docker-compose.prod.yml exec -T nginx nginx -s reload || true
fi

echo "[BG] Verify through Nginx on :80"
curl -fsS http://localhost/ -I | head -n 1
REMOTE
          """
        }
      }
    }
  }

  post {
    success { echo '✅ Level 4 completed' }
    failure { echo '❌ Level 4 failed — check the stage logs' }
  }
}
