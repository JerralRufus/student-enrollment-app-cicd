// This is the final, working Jenkinsfile for the Student Enrollment App.
// It assumes that the Jenkins agent has Docker installed and the 'jenkins' user
// has been given permission to use the Docker socket.
// It works without the "Docker Pipeline" plugin.

pipeline {
    // This pipeline will run on any available agent.
    agent any

    environment {
        // Fetch credentials from Jenkins Credentials Manager by the ID 'dockerhub-credentials'.
        DOCKER_CREDS = credentials('dockerhub-credentials')
        // Construct the image name using the username part from the credentials variable.
        DOCKER_IMAGE_NAME = "${env.DOCKER_CREDS_USR}/student-enrollment-app"
    }

    stages {
        stage('Checkout') {
            steps {
                // The actual checkout from Git is handled automatically by the Jenkins job's SCM configuration.
                // This stage is a placeholder to clearly show this step in the pipeline UI.
                echo "Code checked out from branch: ${env.BRANCH_NAME}"
            }
        }
        
        stage('Install Dependencies & Test') {
            steps {
                script {
                    // This command runs all test steps inside a temporary Docker container.
                    // This keeps the Jenkins agent clean and ensures a consistent test environment.
                    //
                    // Command Breakdown:
                    //   docker run:      Starts a new container.
                    //   --rm:            Automatically removes the container when it exits (crucial for cleanup).
                    //   -v "${pwd()}":/app: Mounts the Jenkins workspace (your code) into the /app directory inside the container.
                    //   -w /app:         Sets the working directory inside the container to /app, where pyproject.toml is located.
                    //   python:3.9-slim: The Docker image to use for testing.
                    //   sh -c '...':     The shell command to execute inside the container.
                    sh """
                    docker run --rm -v "${pwd()}":/app -w /app python:3.9-slim sh -c ' \\
                        echo "--- Installing dependencies ---" && \\
                        pip install --no-cache-dir poetry && \\
                        poetry config virtualenvs.create false && \\
                        poetry install --no-root --no-interaction && \\
                        echo "--- Running tests ---" && \\
                        poetry run pytest'
                    """
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // The build context is '.' which means the current directory (the workspace root),
                    // where the Dockerfile is located.
                    echo "Building Docker image from context: ${pwd()}"
                    sh "docker build -t ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER} ."
                    
                    echo "Tagging image as 'latest' for deployment"
                    // The 'latest' tag is a pointer to the most recent successful build.
                    sh "docker tag ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER} ${DOCKER_IMAGE_NAME}:latest"
                }
            }
        }

        stage('Push Docker Image to Docker Hub') {
            steps {
                echo "Logging into Docker Hub as ${env.DOCKER_CREDS_USR}..."
                // Use the username (_USR) and password (_PSW) from the credentials variable.
                sh "docker login -u ${env.DOCKER_CREDS_USR} -p ${env.DOCKER_CREDS_PSW}"
                
                echo "Pushing tag: ${env.BUILD_NUMBER}"
                sh "docker push ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}"
                
                echo "Pushing tag: latest"
                sh "docker push ${DOCKER_IMAGE_NAME}:latest"
            }
        }
        
        stage('Deploy with Ansible') {
            steps {
                // This stage requires the 'Ansible' plugin to be installed in Jenkins.
                // It executes the playbook to deploy the new container.
                // The 'extraVars' map overrides variables defined inside the playbook.
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
    
    // The 'post' block defines actions that run after the main stages are complete.
    post {
        always {
            // This is a good practice to clean up the workspace, saving disk space.
            cleanWs()
            echo 'Pipeline finished successfully.'
        }
    }
}
