// FINAL WORKING Jenkinsfile - Based on diagnostic log proof.
// This version uses a robust multi-stage Docker build process.
pipeline {
    // Run on any available agent that has Docker installed and configured.
    agent any

    stages {
        stage('1. Cleanup Workspace') {
            steps {
                // This is a crucial first step to prevent issues from old files.
                // It ensures every build starts in a completely clean directory.
                echo "Cleaning workspace to ensure a fresh build..."
                cleanWs()
            }
        }

        stage('2. Checkout Code') {
            steps {
                // This will check out the code from the Git repository configured
                // in the Jenkins job's SCM section.
                echo "Checking out source code from Git..."
                checkout scm
            }
        }
        
        stage('3. Build & Test Docker Image') {
            steps {
                script {
                    // This single command now builds the application image.
                    // The new multi-stage Dockerfile will handle installing dependencies,
                    // running tests, and creating a final, optimized production image.
                    // If the tests inside the Dockerfile fail, this 'docker build' command
                    // will fail, correctly stopping the pipeline.
                    echo "Building the application Docker image via multi-stage build..."
                    sh "docker build -t ${env.DOCKER_USER}/student-enrollment-app:${env.BUILD_NUMBER} ."
                    
                    echo "Tagging the new image as 'latest' for deployment..."
                    sh "docker tag ${env.DOCKER_USER}/student-enrollment-app:${env.BUILD_NUMBER} ${env.DOCKER_USER}/student-enrollment-app:latest"
                }
            }
        }

        stage('4. Push Docker Image to Docker Hub') {
            steps {
                // This block securely uses the credentials with ID 'dockerhub-credentials'.
                // Make sure you have created these credentials in Jenkins.
                echo "Logging into Docker Hub..."
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', passwordVariable: 'DOCKER_PASSWORD', usernameVariable: 'DOCKER_USERNAME')]) {
                    sh "docker login -u ${DOCKER_USERNAME} -p ${DOCKER_PASSWORD}"
                    
                    echo "Pushing build-specific tag: ${env.BUILD_NUMBER}"
                    sh "docker push ${DOCKER_USERNAME}/student-enrollment-app:${env.BUILD_NUMBER}"
                    
                    echo "Pushing 'latest' tag..."
                    sh "docker push ${DOCKER_USERNAME}/student-enrollment-app:latest"
                }
            }
        }
        
        stage('5. Deploy with Ansible') {
            steps {
                // This stage requires the 'Ansible' plugin in Jenkins.
                // It runs the playbook, passing the image name as a variable.
                echo "Deploying the new container with Ansible..."
                ansiblePlaybook(
                    playbook: 'ansible/deploy.yml',
                    inventory: 'ansible/hosts',
                    extraVars: [
                        docker_image: "${env.DOCKER_USER}/student-enrollment-app:latest"
                    ]
                )
            }
        }
    }
    
    post {
        always {
            // This runs after all stages, regardless of success or failure.
            echo 'Pipeline finished.'
        }
    }
}
