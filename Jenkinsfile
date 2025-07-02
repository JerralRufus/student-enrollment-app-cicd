// FINAL, CORRECTED Jenkinsfile - Fixes variable inconsistency for Docker username.
pipeline {
    agent any

    // This is the key change. We define credentials here once, and they become
    // available as environment variables to ALL stages.
    environment {
        DOCKER_CREDS = credentials('dockerhub-credentials')
    }

    stages {
        stage('1. Cleanup Workspace') {
            steps {
                echo "Cleaning workspace to ensure a fresh build..."
                cleanWs()
            }
        }

        stage('2. Checkout Code') {
            steps {
                echo "Checking out source code from Git..."
                checkout scm
            }
        }
        
        stage('3. Build & Test Docker Image') {
            steps {
                script {
                    echo "Building the application Docker image..."
                    // We now use the consistent ${DOCKER_CREDS_USR} variable.
                    // Jenkins automatically provides _USR for username and _PSW for password.
                    sh "docker build -t ${DOCKER_CREDS_USR}/student-enrollment-app:${env.BUILD_NUMBER} ."
                    
                    echo "Tagging the new image as 'latest' for deployment..."
                    // Use the same consistent variable for tagging.
                    sh "docker tag ${DOCKER_CREDS_USR}/student-enrollment-app:${env.BUILD_NUMBER} ${DOCKER_CREDS_USR}/student-enrollment-app:latest"
                }
            }
        }

        stage('4. Push Docker Image to Docker Hub') {
            steps {
                // We no longer need a separate withCredentials block here.
                echo "Logging into Docker Hub as ${DOCKER_CREDS_USR}..."
                sh "docker login -u ${DOCKER_CREDS_USR} -p ${DOCKER_CREDS_PSW}"
                
                echo "Pushing build-specific tag: ${env.BUILD_NUMBER}"
                sh "docker push ${DOCKER_CREDS_USR}/student-enrollment-app:${env.BUILD_NUMBER}"
                
                echo "Pushing 'latest' tag..."
                sh "docker push ${DOCKER_CREDS_USR}/student-enrollment-app:latest"
            }
        }
        
        stage('5. Deploy with Ansible') {
            steps {
                echo "Deploying the new container with Ansible..."
                ansiblePlaybook(
                    playbook: 'ansible/deploy.yml',
                    inventory: 'ansible/hosts',
                    extraVars: [
                        // Use the same consistent variable here too.
                        docker_image: "${DOCKER_CREDS_USR}/student-enrollment-app:latest"
                    ]
                )
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline finished.'
        }
    }
}
