pipeline {
    agent any
    
    environment {
        BMC_URL = 'https://qemu-openbmc:2443'
        BMC_USERNAME = 'root'
        BMC_PASSWORD = '0penBmc'
        PYTHON_VERSION = '3.9'
    }
    
    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '5'))
    }
    
    stages {
        stage('Setup Environment') {
            steps {
                script {
                    echo ' Setting up CI/CD environment for OpenBMC testing'
                    sh '''
                        echo "Python: $(python --version 2>&1 || echo 'not found')"
                        echo "Pip: $(pip --version 2>&1 || echo 'not found')"
                        echo "Docker: $(docker --version 2>&1 || echo 'not found')"
                        echo "Docker Compose: $(docker-compose --version 2>&1 || echo 'not found')"
                    '''
                }
            }
        }
        
        stage('Start Infrastructure') {
            steps {
                script {
                    echo ' Starting Docker containers'
                    sh '''
                        docker-compose up -d
                        echo "Waiting for containers to start..."
                        sleep 10
                    '''
                }
            }
        }
        
        stage('Wait for BMC Ready') {
            steps {
                script {
                    echo ' Waiting for OpenBMC to be ready...'
                    retry(15) {
                        sh '''
                            curl -k -f -u ${BMC_USERNAME}:${BMC_PASSWORD} ${BMC_URL}/redfish/v1/ || exit 1
                        '''
                    }
                    echo ' OpenBMC is ready!'
                }
            }
        }
        
        stage('Install Dependencies') {
            steps {
                script {
                    echo ' Installing Python dependencies'
                    sh '''
                        pip install -r requirements.txt
                        pip list | grep -E "(pytest|requests|locust|selenium)"
                    '''
                }
            }
        }
        
        stage('Run Comprehensive Tests') {
            steps {
                script {
                    echo ' Running comprehensive test suite'
                    sh '''
                        python run_tests.py
                    '''
                }
            }
            post {
                always {
                    junit 'test-results/*.xml'
                    archiveArtifacts artifacts: 'test-results/**/*', allowEmptyArchive: true
                }
            }
        }
        
        stage('Run Additional Security Scan') {
            steps {
                script {
                    echo ' Running additional security scans'
                    sh '''
                        # Run bandit security scanner
                        python -m bandit -r . -f xml -o test-results/bandit-security.xml || true
                        
                        # Run safety for dependency checks
                        python -m safety check --json --output test-results/safety-report.json || true
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'test-results/bandit-security.xml,test-results/safety-report.json', allowEmptyArchive: true
                }
            }
        }
        
        stage('Generate Test Report') {
            steps {
                script {
                    echo ' Generating test reports'
                    sh '''
                        # Create summary report
                        echo "Test Execution Summary" > test-results/summary.txt
                        echo "=====================" >> test-results/summary.txt
                        echo "Timestamp: $(date)" >> test-results/summary.txt
                        echo "BMC URL: ${BMC_URL}" >> test-results/summary.txt
                        echo "Python Version: $(python --version 2>&1)" >> test-results/summary.txt
                        
                        # Check if test result files exist
                        if [ -f "test-results/api-tests.xml" ]; then
                            echo "API Tests: Completed" >> test-results/summary.txt
                        else
                            echo "API Tests: Not executed" >> test-results/summary.txt
                        fi
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'test-results/summary.txt', allowEmptyArchive: true
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'test-results',
                        reportFiles: '**/*.html',
                        reportName: 'HTML Test Report'
                    ])
                }
            }
        }
    }
    
    post {
        always {
            script {
                echo ' Cleaning up environment'
                sh '''
                    echo "Stopping containers..."
                    docker-compose down --remove-orphans || true
                    
                    echo "Cleaning up test files..."
                    rm -f simple_api_test.py 2>/dev/null || true
                '''
            }
        }
        success {
            script {
                echo ' All tests passed!'
                // Uncomment and configure email if needed
                /*
                emailext (
                    subject: "OpenBMC CI/CD Pipeline SUCCESS - ${env.JOB_NAME}",
                    body: "All tests passed successfully!\nBuild URL: ${env.BUILD_URL}",
                    to: "developer@example.com"
                )
                */
            }
        }
        failure {
            script {
                echo ' Pipeline failed!'
                // Uncomment and configure email if needed
                /*
                emailext (
                    subject: "OpenBMC CI/CD Pipeline FAILED - ${env.JOB_NAME}",
                    body: "Pipeline failed. Please check the build logs.\nBuild URL: ${env.BUILD_URL}",
                    to: "developer@example.com"
                )
                */
            }
        }
        unstable {
            script {
                echo ' Pipeline unstable!'
            }
        }
    }
}