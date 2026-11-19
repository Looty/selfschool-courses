// vars/buildPythonService.groovy (lesson l29)
// A custom step in a shared library: the file name is the step name, and call() is what runs.
// It lints once, then tests on every requested Python version in parallel, each in its own container.
//
// The whole Jenkinsfile of a service repository can then be two lines (Scripted style):
//
//   @Library('platform-lib@v1.4.0') _
//   buildPythonService(pythonVersions: ['3.12', '3.13'])

def call(Map config = [:]) {
    // Named arguments arrive as one Map; ?: supplies a default when a key is missing.
    List versions = config.pythonVersions ?: ['3.13']
    String label = config.label ?: 'docker'
    String requirements = config.requirements ?: 'requirements-dev.txt'

    stage('Lint') {
        node(label) {
            checkout scm
            docker.image("python:${versions[-1]}-slim").inside {
                // Values from the caller go through the environment, not into the command string.
                withEnv(["REQS=${requirements}"]) {
                    sh '''
                        python -m venv .venv
                        .venv/bin/pip install --quiet -r "$REQS"
                        .venv/bin/ruff check .
                    '''
                }
            }
        }
    }

    def branches = [:]
    for (int i = 0; i < versions.size(); i++) {
        def py = versions[i]
        branches["Python ${py}"] = {
            node(label) {
                checkout scm
                docker.image("python:${py}-slim").inside {
                    withEnv(["REQS=${requirements}", "PY=${py}"]) {
                        try {
                            sh '''
                                python -m venv .venv
                                .venv/bin/pip install --quiet -r "$REQS"
                                .venv/bin/pytest --junitxml="reports/junit-$PY.xml"
                            '''
                        } finally {
                            junit 'reports/*.xml'
                        }
                    }
                }
            }
        }
    }

    stage('Test') {
        parallel branches
    }
}
