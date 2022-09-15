def dockerImage

pipeline {
    options { timestamps () }
    agent {label 'aliyun-slave'}
    environment {
        image_name = "dpcheck_parser"
        docker_registry = "registry.mycyclone.com"
    }
    stages {
        stage('build images') {
            steps {
                script {
                    dockerImage = docker.build("${docker_registry}/test_project/${image_name}:latest",
                            "--label \"GIT_COMMIT=${env.GIT_COMMIT}\""
                            + " --build-arg test_group=${test_group} --build-arg test_env=${test_env}"
                            + " ."
                    )
                }
            }
        }

        stage('Push to docker repository') {
            when {
                branch 'master'
            }
            options { timeout(time: 5, unit: 'MINUTES') }
            steps {
                withDockerRegistry(credentialsId: 'a3428619-6aa7-482d-97b6-72b83c006530', url: "https://${docker_registry}") {
                    script {
                        dockerImage.push('latest')
                    }
                }
            }
        }
    }
    post {
        always{
            script {
                sh 'docker rmi registry.mycyclone.com/test_project/dpcheck_parser:latest'
            }
        }
    }
}
