def imageMap = [
  "development": "staging",
  "master": "latest"
]

def deploymentTagMap = [
  "development": "kompassi-staging",
  "master": "kompassi-deploy"
]

def tempImage = "tracon/kompassi:build-${env.BUILD_NUMBER}"
def finalImage = "tracon/kompassi:${imageMap[env.BRANCH_NAME]}"

stage("Build") {
  node {
    checkout scm
    sh "docker build --tag ${tempImage} ."
  }
}

stage("Test") {
  node {
    sh """
      docker run \
        --rm \
        --link jenkins.tracon.fi-postgres:postgres \
        --env-file ~/.kompassi.env \
        ${tempImage} \
        python manage.py test --keepdb
    """
  }
}

stage("Push") {
  node {
    sh "docker tag ${tempImage} ${finalImage} && docker push ${finalImage} && docker rmi ${tempImage}"
  }
}

stage("Deploy") {
  node {
    git url: "git@github.com:tracon/ansible-tracon"
    sh """
      ansible-playbook \
        --vault-password-file=~/.vault_pass.txt \
        --user root \
        --limit neula.kompassi.eu \
        --tags ${deploymentTagMap[env.BRANCH_NAME]} \
        tracon.yml
    """
  }
}
