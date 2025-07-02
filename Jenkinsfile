// FINAL DIAGNOSTIC Jenkinsfile - This will show us the complete file structure.
pipeline {
    agent any

    stages {
        stage('Investigate Workspace Structure') {
            steps {
                script {
                    echo "================== START OF DIAGNOSTIC =================="
                    echo "Jenkins is running this job in the following directory on the host:"
                    sh 'pwd'

                    echo "\n\n--- Recursive File Listing ---"
                    echo "This shows every file and folder in the workspace. We are looking for the location of 'pyproject.toml'."
                    // The 'ls -R' command lists files recursively.
                    // The '|| true' part ensures the build doesn't fail if a folder is empty.
                    sh 'ls -R || true'
                    echo "=================== END OF DIAGNOSTIC ==================="
                }
            }
        }
    }
}
