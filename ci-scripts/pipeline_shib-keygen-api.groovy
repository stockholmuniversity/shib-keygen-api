#!/usr/bin/env groovy

def projectName = env.JOB_NAME
def moduleName = projectName.replaceAll("-", "_")
def revision
def tag


suSetProperties(["github": "true"])

node("agent") {
    stage("Cleanup workspace")
    {
        cleanWs()
    }

    stage("Prepare docker environment")
    {
        suDockerBuildAndPull(projectName)
    }

    docker.image(projectName).inside('-v /var/run/docker.sock:/var/run/docker.sock -v /local/jenkins/conf:/local/jenkins/conf -v /local/jenkins/libexec:/local/jenkins/libexec -v /etc/pip.conf:/etc/pip.conf') {
        suGitHubBuildStatus {

            stage("Get information")
            {
                revision = env.rev ?: sh(script: "git log -n 1  --pretty=format:'%H'", returnStdout: true).trim()
                tag = sh(script: "tag=\$(git tag --contains ${revision} | tail -1); if [ \"${env.branch}\" = \"\$tag\" ]; then echo \$tag; fi", returnStdout: true).trim()
            }

            suWithPoetryCredentials(tag: tag) {
                sh(script: "poetry install --all-extras")
                sh(script: "python3 -m poetry run python3 -m pylint ${moduleName}")
                sh(script: "python3 -m poetry run python3 -m black --check --diff .")
                sh(script: "python3 -m poetry run python3 -m isort --check --diff .")
                sh(script: "python3 -m poetry run python3 -m mypy ${moduleName}")
                sh(script: "python3 -m poetry run python3 -m pytest")
            }

            stage("Build and push docker image") {
                String dockerRegistry = suGetConfVariable 'docker_registry'
                docker.withRegistry('https://' + dockerRegistry, 'su-docker-private') {
                    if (tag) {
                        build_args = "--build-arg TAG=${tag} --target prod"
                    }
                    else {
                        build_args = "--target dev"
                    }
                    withEnv(['DOCKER_BUILDKIT=1']) {
                        app = docker.build(projectName, "--build-arg PROJECT=${moduleName} ${build_args} --pull .")
                    }
                    if (tag) {
                        app.push(tag)
                    } else {
                        app.push("latest")
                    }
                }
            }
        }
    }
}
