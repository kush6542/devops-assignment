pipeline {
    agent any

    environment {
        APP_IMAGE = "aceest-app"
    }

    stages {
        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Install & Lint') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements-dev.txt
                    python -m py_compile app.py
                    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics --exclude=venv
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest tests/ -v
                '''
            }
        }

        stage('Build Docker') {
            steps {
                sh "docker build --target test -t ${APP_IMAGE}:test-${BUILD_NUMBER} ."
                sh "docker build --target runtime -t ${APP_IMAGE}:${BUILD_NUMBER} ."
            }
        }

        stage('Test in Container') {
            steps {
                sh "docker run --rm ${APP_IMAGE}:test-${BUILD_NUMBER}"
            }
        }
    }

    post {
        always {
            sh "docker rmi ${APP_IMAGE}:test-${BUILD_NUMBER} || true"
            cleanWs()
        }
    }
}
