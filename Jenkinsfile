// DEBUGGING Jenkinsfile - This file's only purpose is to list the directory structure.
pipeline {
    agent any

    stages {
        stage('Checkout') {
            // Jenkins automatically checks out the code here based on your job config.
            steps {
                echo "Code has been checked out."
            }
        }

        stage('Investigate Workspace') {
            steps {
                script {
                    echo "--- Listing files in the TOP-LEVEL workspace: ${pwd()} ---"
                    // This 'ls' command runs directly on the Jenkins agent.
                    sh 'ls -la'

                    echo "\n\n--- Running a container and listing files INSIDE the container's /app directory ---"
                    // This 'ls' runs inside the temporary container we use for testing.
                    sh """
                    docker run --rm -v "${pwd()}":/app -w /app python:3.9-slim sh -c ' \\
                        echo "--- Current directory inside container is: \$(pwd) ---"; \\
                        ls -la'
                    """
                }
            }
        }
    }
}
