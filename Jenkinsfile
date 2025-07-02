// FINAL, DEBUGGED Jenkinsfile
// This version assumes pyproject.toml and Dockerfile are in the root of the repository.
pipeline {
    agent any

    environment {
        DOCKER_CREDS = credentials('dockerhub-credentials')
        DOCKER_IMAGE_NAME = "${env.DOCKER_CREDS_USR}/student-enrollment-app"
    }

    stages {
        stage('Checkout') {
            steps {
                echo "Code checked out from branch: ${env.BRANCH_NAME}"
            }
        }
        
        stage('Install Dependencies & Test') {
            steps {
                script {
                    // We mount the workspace to /app and set the working directory to /app
                    // We then add a debugging 'ls -la' command to see the file structure
                    sh """
                    docker run --rm -v "${pwd()}":/app -w /app python:3.9-slim sh -c ' \\
                        echo "--- Listing files in the workspace (/app) ---" && \\
                        ls -la && \\
                        echo "--- Installing dependencies ---" && \\
                        pip install poetry && \\
                        poetry config virtualenvs.create false && \\
                        poetry install --no-root && \\
                        echo "--- Running tests ---" && \\
                        poetry run pytest'
                    """
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // The build context is now simply the workspace root, which is '.'.
                    echo "Building Docker image from context: ${pwd()}"
                    sh "docker build -t ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER} ."
                    
                    echo "Tagging image as 'latest'"
                    sh "docker tag ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER} ${DOCKER_IMAGE_NAME}:latest"
                }
            }
        }

        stage('Push Docker Image to Docker Hub') {
            steps {
                echo "Logging into Docker Hub..."
                sh "docker login -u ${env.DOCKER_CREDS_USR} -p ${env.DOCKER_CREDS_PSW}"
                
                echo "Pushing tag: ${env.BUILD_NUMBER}"
                sh "docker push ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}"
                
                echo "Pushing tag: latest"
                sh "docker push ${DOCKER_IMAGE_NAME}:latest"
            }
        }
        
        stage('Deploy with Ansible') {
            steps {
                // Ansible playbook path is now directly in the root
                ansiblePlaybook(
                    playbook: 'ansible/deploy.yml',
                    inventory: 'ansible/hosts',
                    extraVars: [
                        docker_image: "${DOCKER_IMAGE_NAME}:latest"
                    ]
                )
            }
        }
    }
    
    post {
        always {
            cleanWs()
            echo 'Pipeline finished.'
        }
    }
}
