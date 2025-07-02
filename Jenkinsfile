// Updated and Simplified Jenkinsfile
// Assumes:
// 1. "Docker Pipeline" plugin is installed in Jenkins.
// 2. The Jenkins job is configured for SCM with the correct repository URL and branch ("*/main").

pipeline {
    // Defines the default agent for all stages.
    // We use a node with the label 'docker' to ensure Docker is available.
    // If your main Jenkins node has Docker, 'any' will also work.
    agent any

    // Environment variables available to all stages
    environment {
        // Fetches the Docker Hub credentials from Jenkins Credentials Manager
        DOCKER_CREDS = credentials('dockerhub-credentials')
        // Uses the username part of the credentials to construct the image name
        DOCKER_IMAGE_NAME = "${env.DOCKER_CREDS_USR}/student-enrollment-app"
    }

    stages {
        // Stage 1: Checkout
        // This stage is now just for show. The actual checkout is done automatically
        // by Jenkins before the pipeline starts, based on the job's SCM configuration.
        stage('Checkout') {
            steps {
                echo "Code automatically checked out from branch: ${env.BRANCH_NAME}"
            }
        }

        // Stage 2: Build & Test
        // This stage runs its steps inside a temporary Docker container.
        // The container is automatically started and stopped by the Docker Pipeline plugin.
        stage('Build & Test') {
            agent {
                // Use a standard Python image to run our build and test steps
                docker { image 'python:3.9-slim' }
            }
            steps {
                echo 'Installing dependencies and running tests inside a Docker container...'
                // These shell commands run inside the 'python:3.9-slim' container
                sh 'pip install poetry'
                sh 'poetry config virtualenvs.create false'
                sh 'poetry install --no-root'
                sh 'poetry run pytest'
            }
        }

        // Stage 3: Build Docker Image
        // This stage builds the actual application image that will be deployed.
        stage('Build Docker Image') {
            steps {
                script {
                    // Build the image using the Dockerfile in our repository
                    // Tag it with the unique Jenkins build number for versioning
                    sh "docker build -t ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER} ."
                    // Also tag the same image as 'latest' for easy deployment
                    sh "docker tag ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER} ${DOCKER_IMAGE_NAME}:latest"
                }
            }
        }

        // Stage 4: Push Docker Image to Docker Hub
        stage('Push Docker Image') {
            steps {
                // The 'DOCKER_CREDS' environment variable is a special credential type.
                // We use it directly for docker login. Jenkins handles injecting the username and password.
                sh "docker login -u ${env.DOCKER_CREDS_USR} -p ${env.DOCKER_CREDS_PSW}"
                // Push both the build-specific tag and the 'latest' tag
                sh "docker push ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}"
                sh "docker push ${DOCKER_IMAGE_NAME}:latest"
            }
        }

        // Stage 5: Deploy with Ansible
        // This stage runs the deployment playbook.
        stage('Deploy with Ansible') {
            steps {
                // Ensure the 'Ansible' plugin is installed in Jenkins.
                // We pass the image name and 'latest' tag to the playbook.
                // This ensures Ansible deploys the image we just built and pushed.
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

    // Post-build actions that run regardless of the pipeline's success or failure
    post {
        always {
            // Clean up the workspace to save disk space
            cleanWs()
            echo 'Pipeline finished.'
        }
    }
}
