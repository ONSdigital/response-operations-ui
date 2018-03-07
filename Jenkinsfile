pipeline {
    agent any

    triggers {
        pollSCM('* * * * *')
    }

    stages {

        stage('dev') {
            agent {
                docker {
                    image 'governmentpaas/cf-cli'
                    args '-u root'
                }
            }

            environment {
                CLOUDFOUNDRY_API = credentials('CLOUDFOUNDRY_API')
                CF_DOMAIN = credentials('CF_DOMAIN')
                DEV_SECURITY = credentials('DEV_SECURITY')
                CF_USER = credentials('CF_USER')
            }
            steps {
                sh "cf login -a https://${env.CLOUDFOUNDRY_API} --skip-ssl-validation -u ${CF_USER_USR} -p ${CF_USER_PSW} -o rmras -s dev"
                sh 'cf push --no-start response-operations-ui-dev'
                sh 'cf set-env response-operations-ui-dev ONS_ENV dev'
                sh 'cf set-env response-operations-ui-dev REDIS_SERVICE ras-redis'
                sh "cf set-env response-operations-ui-dev BACKSTAGE_API_URL http://ras-backstage-service-dev.${env.CF_DOMAIN}:80/backstage-api"
                sh 'cf start response-operations-ui-dev'
            }
        }

        stage('ci?') {
            agent none
            steps {
                script {
                    try {
                        timeout(time: 60, unit: 'SECONDS') {
                            script {
                                env.deploy_ci = input message: 'Deploy to CI?', id: 'deploy_ci', parameters: [choice(name: 'Deploy to CI', choices: 'no\nyes', description: 'Choose "yes" if you want to deploy to CI')]
                            }
                        }
                    } catch (ignored) {
                        echo 'Skipping ci deployment'
                    }
                }
            }
        }

        stage('ci') {
            agent {
                docker {
                    image 'governmentpaas/cf-cli'
                    args '-u root'
                }

            }
            when {
                environment name: 'deploy_ci', value: 'yes'
            }

            environment {
                CLOUDFOUNDRY_API = credentials('CLOUDFOUNDRY_API')
                CF_DOMAIN = credentials('CF_DOMAIN')
                CI_SECURITY = credentials('CI_SECURITY')
                CF_USER = credentials('CF_USER')
            }
            steps {
                sh "cf login -a https://${env.CLOUDFOUNDRY_API} --skip-ssl-validation -u ${CF_USER_USR} -p ${CF_USER_PSW} -o rmras -s ci"
                sh 'cf push --no-start response-operations-ui-ci'
                sh 'cf set-env response-operations-ui-test ONS_ENV ci'
                sh 'cf set-env response-operations-ui-dev REDIS_SERVICE ras-redis'
                sh "cf set-env response-operations-ui-ci BACKSTAGE_API_URL http://ras-backstage-service-ci.${env.CF_DOMAIN}:80/backstage-api"
                sh 'cf start response-operations-ui-ci'
            }
        }

        stage('release?') {
            agent none
            steps {
                script {
                    try {
                        timeout(time: 60, unit: 'SECONDS') {
                            script {
                                env.do_release = input message: 'Do a release?', id: 'do_release', parameters: [choice(name: 'Deploy to test', choices: 'no\nyes', description: 'Choose "yes" if you want to create a tag')]
                            }
                        }
                    } catch (ignored) {
                        echo 'Skipping test deployment'
                    }
                }
            }
        }

        stage('release') {
            agent {
                docker {
                    image 'node'
                    args '-u root'
                }

            }
            environment {
                GITHUB_API_KEY = credentials('GITHUB_API_KEY')
            }
            when {
                environment name: 'do_release', value: 'yes'
            }
            steps {
                // Prune any local tags created by any other builds
                sh "git tag -l | xargs git tag -d && git fetch -t"
                sh "git remote set-url origin https://ons-sdc:${GITHUB_API_KEY}@github.com/ONSdigital/response-operations-ui.git"
                sh "npm install -g bmpr"
                sh "bmpr patch|xargs git push origin"
            }
        }

        stage('test') {
            agent {
                docker {
                    image 'governmentpaas/cf-cli'
                    args '-u root'
                }

            }
            when {
                environment name: 'do_release', value: 'yes'
            }

            environment {
                CLOUDFOUNDRY_API = credentials('CLOUDFOUNDRY_API')
                CF_DOMAIN = credentials('CF_DOMAIN')
                TEST_SECURITY = credentials('TEST_SECURITY')
                CF_USER = credentials('CF_USER')
            }
            steps {
                sh "cf login -a https://${env.CLOUDFOUNDRY_API} --skip-ssl-validation -u ${CF_USER_USR} -p ${CF_USER_PSW} -o rmras -s test"
                sh 'cf push --no-start response-operations-ui-test'
                sh 'cf set-env response-operations-ui-test ONS_ENV test'
                sh 'cf set-env response-operations-ui-dev REDIS_SERVICE ras-redis'
                sh "cf set-env response-operations-ui-test BACKSTAGE_API_URL http://ras-backstage-service-test.${env.CF_DOMAIN}:80/backstage-api"
                sh 'cf start response-operations-ui-test'
            }
        }
    }

    post {
        always {
            cleanWs()
            dir('${env.WORKSPACE}@tmp') {
                deleteDir()
            }
            dir('${env.WORKSPACE}@script') {
                deleteDir()
            }
            dir('${env.WORKSPACE}@script@tmp') {
                deleteDir()
            }
        }
    }
}