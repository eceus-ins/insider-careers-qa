pipeline {
    agent any

    environment {
        DB_HOST     = 'localhost'
        DB_PORT     = '3307'
        DB_NAME     = 'test_results_db'
        DB_USER     = 'test_user'
        DB_PASSWORD = credentials('mysql-test-password')
        BRANCH_NAME = "${env.GIT_BRANCH ?: 'local'}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                dir('insider_automation_tests') {
                    sh 'pip3 install -r requirements.txt --break-system-packages'
                }
            }
        }

        stage('Run UI Tests') {
            steps {
                dir('insider_automation_tests') {
                    sh 'mkdir -p reports screenshots'
                    sh '''
                        python3 -m pytest \
                            --browser=chrome \
                            --headless \
                            --junitxml=reports/junit.xml \
                            -v
                    '''
                }
            }
        }
    }

    post {
        always {
            junit 'insider_automation_tests/reports/junit.xml'
            archiveArtifacts artifacts: 'insider_automation_tests/reports/**, insider_automation_tests/screenshots/**', allowEmptyArchive: true
            echo "Build ${env.BUILD_NUMBER} tamamlandi: ${currentBuild.result}. Sonuclar test_results_db'ye yazildi, Grafana: http://localhost:3000/d/qa-test-metrics"
        }
        failure {
            echo "Testler basarisiz - Grafana dashboard kontrol edilmeli"
        }
    }
}
