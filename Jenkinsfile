// This Jenkinsfile uses manual docker commands instead of the 'agent { docker ... }' syntax.
// It requires the Jenkins agent to have Docker installed and the Jenkins user to have permission to use it.
pipeline {
    agent any

    environment {
        DOCKER_CREDS = credentials('dockerhub-credentials')
        // We will tag with the build number to ensure uniqueness
        DOCKER_IMAGE_NAME = "${env.DOCKER_CREDS_USR}/student-enrollment-app"
        DOCKER_IMAGE_TAG = "build-${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/JerralRufus/student-enrollment-app-cicd.git'
            }
        }
        
        stage('Install Dependencies & Test') {
            steps {
                script {
                    // Manually run the tests inside a temporary Docker container
                    // -v mounts the current Jenkins workspace into the container's /app directory
                    // -w sets the working directory inside the container
                    // --rm automatically cleans up the container after it exits
                    sh """
                    docker run --rm -v "${pwd}":/app -w /app python:3.9-slim sh -c ' \
                        pip install poetry && \
                        poetry config virtualenvs.create false && \
                        poetry install --no-root && \
                        poetry run pytest'
                    """
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Build the image and tag it with our build number
                    sh "docker build -t ${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG} ."
                    // Also tag it as 'latest' for convenience
                    sh "docker tag ${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG} ${DOCKER_IMAGE_NAME}:latest"
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                // Jenkins will automatically use the username (_USR) and password (_PSW)
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', passwordVariable: 'DOCKERHUB_PASSWORD', usernameVariable: 'DOCKERHUB_USERNAME')]) {
                    sh "docker login -u ${DOCKERHUB_USERNAME} -p ${DOCKERHUB_PASSWORD}"
                    // Push both the build-specific tag and the 'latest' tag
                    sh "docker push ${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}"
                    sh "docker push ${DOCKER_IMAGE_NAME}:latest"
                }
            }
        }
        
        stage('Deploy with Ansible') {
            steps {
                // Ensure Ansible plugin is installed on Jenkins
                // Deploy using the 'latest' tag for simplicity
                ansiblePlaybook(
                    playbook: 'ansible/deploy.yml',
                    inventory: 'ansible/hosts',
                    extraVars: [
                        docker_image: "${DOCKER_IMAGE_NAME}:latest" // Override with the image we just pushed
                    ]
                )
            }
        }
    }
}
