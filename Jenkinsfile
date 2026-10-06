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
                    python3 -m venv venv || true
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
                '''
            }
        }

        stage('Build Docker') {
            steps {
                sh "docker build -t ${APP_IMAGE}:${BUILD_NUMBER} ."
            }
        }

        stage('Test in Container') {
            steps {
                sh "docker run --rm ${APP_IMAGE}:${BUILD_NUMBER} pytest tests/ -v"
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
