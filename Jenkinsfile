// This Jenkinsfile works WITHOUT the Docker Pipeline plugin.
// It uses standard shell commands to interact with Docker.
// It requires that the Jenkins agent has Docker installed.
pipeline {
    // This pipeline will run on any available agent.
    agent any

    environment {
        // Fetch credentials from Jenkins Credentials Manager by ID.
        DOCKER_CREDS = credentials('dockerhub-credentials')
        // Construct the image name using the username from the credentials.
        DOCKER_IMAGE_NAME = "${env.DOCKER_CREDS_USR}/student-enrollment-app"
    }

    stages {
        stage('Checkout') {
            steps {
                // The actual checkout is handled by the Jenkins job configuration.
                // This is just a placeholder to show the stage in the UI.
                echo "Code checked out from branch: ${env.BRANCH_NAME}"
            }
        }
        
        stage('Install Dependencies & Test') {
            steps {
                // We will manually run our tests inside a temporary Python container.
                script {
                    // This command does the following:
                    //   docker run:      Starts a new container
                    //   --rm:            Automatically removes the container when it exits (very important for cleanup)
                    //   -v "${pwd()}":/app: Mounts the current Jenkins workspace directory (your code) into the /app directory inside the container
                    //   -w /app:         Sets the working directory inside the container to /app
                    //   python:3.9-slim: The Docker image to use for this container
                    //   sh -c '...':     The shell command to execute inside the container
                    sh """
                    docker run --rm -v "${pwd()}":/app -w /app python:3.9-slim sh -c ' \\
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
                    echo "Building Docker image: ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}"
                    // Build the image using the Dockerfile from our repository
                    sh "docker build -t ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER} ."
                    
                    echo "Tagging image as 'latest'"
                    // Also tag the same image as 'latest' for the deployment step
                    sh "docker tag ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER} ${DOCKER_IMAGE_NAME}:latest"
                }
            }
        }

        stage('Push Docker Image to Docker Hub') {
            steps {
                echo "Logging into Docker Hub..."
                // Use the username and password from the credentials variable
                sh "docker login -u ${env.DOCKER_CREDS_USR} -p ${env.DOCKER_CREDS_PSW}"
                
                echo "Pushing tag: ${env.BUILD_NUMBER}"
                sh "docker push ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}"
                
                echo "Pushing tag: latest"
                sh "docker push ${DOCKER_IMAGE_NAME}:latest"
            }
        }
        
        stage('Deploy with Ansible') {
            steps {
                // This stage uses the Ansible plugin, which is separate from the Docker plugin.
                // It passes the name of the 'latest' image to the playbook.
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
    
    // This 'post' block runs after all stages are complete.
    post {
        always {
            // This is good practice to clean up the workspace.
            cleanWs()
            echo 'Pipeline finished.'
        }
    }
}
