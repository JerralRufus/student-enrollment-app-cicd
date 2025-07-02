// This Jenkinsfile works WITHOUT the Docker Pipeline plugin.
// It uses standard shell commands to interact with Docker.
// **CORRECTED VERSION**
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
                    // The key change is here: -w /app/student-enrollment-app
                    // This sets the working directory to where pyproject.toml is located.
                    sh """
                    docker run --rm -v "${pwd()}":/app -w /app/student-enrollment-app python:3.9-slim sh -c ' \\
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
                    echo "Building Docker image from context: ${pwd()}/student-enrollment-app"
                    // The key change is here: We specify the build context path explicitly.
                    // The final '.' tells Docker to use the Dockerfile from that directory.
                    sh "docker build -t ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER} ${pwd()}/student-enrollment-app"
                    
                    echo "Tagging image as 'latest'"
                    sh "docker tag ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER} ${DOCKER_IMAGE_NAME}:latest"
                }
            }
        }

        // The Push and Deploy stages remain the same
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
                // We need to tell Ansible where to find its files, since they are also in a subdirectory now.
                ansiblePlaybook(
                    playbook: 'student-enrollment-app/ansible/deploy.yml',
                    inventory: 'student-enrollment-app/ansible/hosts',
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
