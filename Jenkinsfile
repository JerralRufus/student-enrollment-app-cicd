// NOTE: This Jenkinsfile requires Jenkins to have Docker and Ansible installed
// or to run inside a container that has these tools.
pipeline {
    agent any

    environment {
        DOCKER_CREDS = credentials('dockerhub-credentials')
        DOCKER_IMAGE = "${env.DOCKER_CREDS_USR}/student-enrollment-app:${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/JerralRufus/student-enrollment-app-cicd.git'
            }
        }
        
        stage('Install Dependencies & Test') {
            // Run tests inside a python container to keep the Jenkins agent clean
            agent {
                docker { image 'python:3.9-slim' }
            }
            steps {
                sh 'pip install poetry'
                sh 'poetry config virtualenvs.create false'
                sh 'poetry install --no-root'
                sh 'poetry run pytest'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh "docker build -t ${DOCKER_IMAGE} ."
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                // Jenkins will automatically use the username (_USR) and password (_PSW)
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', passwordVariable: 'DOCKERHUB_PASSWORD', usernameVariable: 'DOCKERHUB_USERNAME')]) {
                    sh "docker login -u ${DOCKERHUB_USERNAME} -p ${DOCKERHUB_PASSWORD}"
                    sh "docker push ${DOCKER_IMAGE}"
                }
            }
        }
        
        stage('Deploy with Ansible') {
            steps {
                // Make sure Ansible is installed on the Jenkins agent
                // Note: You may need to configure the host key checking for the first time
                // or disable it for this example.
                ansiblePlaybook(
                    playbook: 'ansible/deploy.yml',
                    inventory: 'ansible/hosts',
                    extraVars: [
                        docker_image: DOCKER_IMAGE // Override the image with the one we just built
                    ]
                )
            }
        }
    }
}
