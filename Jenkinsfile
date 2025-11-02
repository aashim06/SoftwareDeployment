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
        sh '''
          docker build -t groupstudy:${BUILD_NUMBER} .
          docker tag groupstudy:${BUILD_NUMBER} groupstudy:prod
        '''
      }
    }

    stage('Test') {
      steps {
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
          sh 'ssh -o StrictHostKeyChecking=no ec2-user@$EC2_HOST "echo SSH OK && uname -a"'
        }
      }
    }

    stage('Deploy to EC2 (Prod)') {
  steps {
    sshagent(credentials: ['ec2-softdeploy']) {
      sh """
        set -e
        mkdir -p ~/.ssh
        ssh-keyscan -H $EC2_HOST >> ~/.ssh/known_hosts 2>/dev/null || true

        echo "Sync project files to EC2..."
        rsync -az --delete -e "ssh -o StrictHostKeyChecking=no" ./ ec2-user@$EC2_HOST:~/app/

        echo "Start both app slots & nginx..."
        ssh -o StrictHostKeyChecking=no ec2-user@$EC2_HOST '
          cd ~/app &&
          docker compose -f docker-compose.prod.yml up -d --build nginx app_blue app_green
        '

        echo "Determine current active slot..."
        CURRENT=\$(ssh -o StrictHostKeyChecking=no ec2-user@$EC2_HOST "grep -o 'gs_app\\\\(_blue\\\\|_green\\\\)' ~/app/nginx/upstream.conf | sed 's/gs_app_//'")
        if [ "\$CURRENT" = "blue" ]; then TARGET=green; else TARGET=blue; fi
        echo "Current=\$CURRENT → Target=\$TARGET"

        echo "Health check target (inside Nginx container) before switch..."
        ssh -o StrictHostKeyChecking=no ec2-user@$EC2_HOST "
          for i in {1..12}; do
            if docker exec reverse_proxy curl -fsS http://gs_app_\$TARGET:8000/health >/dev/null; then echo healthy; exit 0; fi
            sleep 5
          done
          echo 'Target did not become healthy in time'; exit 1
        "

        echo "Switch Nginx upstream to \$TARGET and reload..."
        ssh -o StrictHostKeyChecking=no ec2-user@$EC2_HOST "
          if [ \"\$TARGET\" = \"blue\" ]; then
            echo 'upstream active_app { server gs_app_blue:8000; }' > ~/app/nginx/upstream.conf
          else
            echo 'upstream active_app { server gs_app_green:8000; }' > ~/app/nginx/upstream.conf
          fi
          docker exec reverse_proxy nginx -s reload || docker compose -f ~/app/docker-compose.prod.yml restart nginx
        "

        echo "Smoke test through the load balancer..."
        curl -fsS http://$EC2_HOST/health >/dev/null

        echo "✅ Blue-green switch complete — new slot: \$TARGET"
      """
    }
  }
}

  }

  post {
    success { echo '✅ Level 4 blue-green deploy completed successfully' }
    failure { echo '❌ Level 4 failed — check the stage logs' }
  }
}
