---
id: l29
title: "Credentials, parallel stages, shared libraries and scripted Groovy"
quiz: quiz-02.yaml
resources: [../resources/ch10/Jenkinsfile.scripted, ../resources/ch10/vars/buildPythonService.groovy]
sources: [142, 143, 144, 145, 147]
---
After this lesson you can pass secrets to a pipeline without leaking them, fan tests out with `parallel` and `matrix`, read and edit a Scripted Pipeline and a shared-library step, and know which Groovy features you actually need for that.

## Credentials

Credentials live in Jenkins and are referred to by id. In Declarative, `credentials()` inside `environment` binds them [143]:

| Credential type | What the variable holds |
| --- | --- |
| Secret text | the secret itself [143] |
| Secret file | path of a temporary file [143] |
| Username and password | `user:pass`, plus `VAR_USR` and `VAR_PSW` [143] [144] |
| SSH private key | path of a temporary key file, plus `VAR_USR` and `VAR_PSW` (the passphrase) [143] |

A variable bound in a stage's `environment` exists only in that stage [144]. For other types, or in Scripted, use `withCredentials`, whose variables exist only inside its block [144]:

```groovy
withCredentials([string(credentialsId: 'registry-token', variable: 'REG_TOKEN')]) {
    sh 'echo "$REG_TOKEN" | docker login -u ci-bot --password-stdin registry.example.internal'
}
```

Jenkins replaces bound secrets with `****` in the console log, but that only stops accidents, not a malicious job; do not let untrusted pipelines use trusted credentials [144].

### Single quotes, always

Groovy expands `${...}` only in double-quoted strings [144]. With `sh "curl -H 'Authorization: Bearer ${API_TOKEN}' ..."` Groovy pastes the secret into the command before it reaches the agent, so it shows in the process list (for example in `ps`), and shell characters in it get executed [144]. With single quotes the shell reads `$API_TOKEN` from its environment [144]. The same rule protects against injection: a parameter set to `hello; ls /` inside `sh("echo ${STATEMENT}")` runs `ls /` [144]. The rule targets secrets and anything a user controls; `Jenkinsfile.scripted` interpolates `${py}` in double quotes because it comes from a constant list in the same file.

The course's test run (Jenkins 2.580.2) bound a secret text as `TOKEN` and ran both forms. The log was masked both times, but Jenkins flagged the double-quoted one:

```text
[Pipeline] sh
Warning: A secret was passed to "sh" using Groovy String interpolation, which is insecure.
		 Affected argument(s) used the following variable(s): [TOKEN]
+ echo token is ****
token is ****
```

## Parallel, matrix, input, stash

`parallel` runs nested stages at once; `failFast true` on the parent stage, or the `parallelsAlwaysFailFast()` option, aborts the rest when one fails [143]. `matrix` generates the stages for you, one cell per combination of `axes`, minus `excludes` [143]:

```groovy
matrix {
    agent { label 'docker' }
    axes {
        axis {
            name 'PYTHON'
            values '3.12', '3.13'
        }
        axis {
            name 'DB'
            values 'sqlite', 'postgres'
        }
    }
    excludes {
        exclude {
            axis {
                name 'PYTHON'
                values '3.12'
            }
            axis {
                name 'DB'
                values 'postgres'
            }
        }
    }
    stages {
        stage('Test') {
            steps {
                sh 'echo "testing on Python $PYTHON with $DB"'
            }
        }
    }
}
```

Two by two is four cells; the exclude removes one, leaving three. A stage holds exactly one of `steps`, `stages`, `parallel` or `matrix`, and you cannot nest `parallel` or `matrix` inside a stage that is already in one [143].

- **`input`** on a stage pauses for approval; `submitter` limits who may approve [143].
- **`stash` / `unstash`** move files between agents in one run, through the controller; stashes are deleted when the run ends [144].
- **`agent { docker { ... } }`** gives a stage a fresh workspace mounted into the container; `reuseNode true` reuses the top-level node and workspace [143] [147]. Containers start clean, so mount a cache directory with `args '-v ...'` if downloads are slow [147].

The snippets above passed the Declarative linter in the test container.

## Scripted Pipeline and the `script` step

Scripted is Groovy run top to bottom: `node('label') { ... }` takes an executor and a workspace, `if`/`else` decides, and a failing step throws an exception, so cleanup goes in `try`/`finally` [142] [143]. Declarative's `script { }` step embeds a piece of Scripted; move anything large into a shared library [143].

`resources/ch10/Jenkinsfile.scripted` is the l28 pipeline in Scripted form:

| Declarative | Scripted equivalent in the file |
| --- | --- |
| `agent { docker { image ... } }` | `node('docker') { docker.image('python:3.13-slim').inside { ... } }` [147] |
| `parallel { stage ... }` | a Map of name to closure, passed to `parallel testBranches` [144] |
| `post { always { junit ... } }` | `try { sh ... } finally { junit ... }` [144] |
| `when { branch 'main' }` | `if (env.BRANCH_NAME == 'main') { stage('Deploy') { ... } }` [143] |
| `post { failure { mail ... } }` | `catch (err) { mail ...; throw err }` [143] [144] |
| `environment { X = ... }` | `withEnv(["IMAGE=${image}"]) { ... }` [144] |

It builds the map with a classic `for` loop. Pipeline serializes its state so runs survive a controller restart, and some idioms such as `collection.each { }` are not fully supported [143].

## Shared libraries

A shared library is a Git repository with this layout [145]:

```text
src/org/example/Helper.groovy   classes, added to the classpath
vars/buildPythonService.groovy  a global variable or custom step named buildPythonService
vars/buildPythonService.txt     its help text
resources/org/example/x.json    files read with libraryResource
```

Load it with `@Library('platform-lib') _`, or pin a version: `@Library('platform-lib@v1.4.0') _` (a branch, tag or commit) [145]. A file in `vars/` with a `call` method becomes a step [145]. `resources/ch10/vars/buildPythonService.groovy` is one: it lints once, then tests every requested Python version in parallel. A service's whole Jenkinsfile becomes:

```groovy
@Library('platform-lib@v1.4.0') _
buildPythonService(pythonVersions: ['3.12', '3.13'])
```

Rules worth remembering:

- Global trusted libraries can call any Jenkins API; whoever can push to that repository effectively controls Jenkins. Folder-level libraries are always untrusted and run in the sandbox. [145]
- In Declarative, calling a method on a library object (`log.info 'x'`) must sit inside `script { }`. [145]
- Keep `vars/` scripts stateless; state is lost on a controller restart. [145]

## Enough Groovy to read a Jenkinsfile

Pipeline code is Groovy, chosen because Jenkins already shipped an embedded Groovy engine [143].

- `'single'` is literal, `"double ${x}"` interpolates [144].
- `sh 'make'` is `sh([script: 'make'])`: parentheses are optional, and named arguments form a Map [144].
- Braces passed to a step, as in `stage('x') { ... }` or `windows { bat "cmd /?" }`, are a block of code the step runs, typed `Closure body` in the docs' custom step [145].
- `def x = ...` declares a variable, as in the docs' `def browsers = ['chrome', 'firefox']` [143].

## Gotchas

- **Double-quoted `sh` with a secret.** The secret reaches the process arguments; single-quote it. [144]
- **Parameters in a GString command.** Shell injection, like SQL injection; single-quote it. [144]
- **`****` is not security.** Masking only hides accidental prints; a job can still exfiltrate the value. [144]
- **`.each` in Pipeline code.** Not fully supported; use a `for` loop. [143]
- **Trusted library repository.** Push access to it is admin access to Jenkins. [145]
- **Method call outside `script`.** `log.info` fails in a Declarative `steps` block. [145]

:::low-confidence
`Jenkinsfile.scripted` and `buildPythonService.groovy` were only syntax-checked: both parsed with Groovy's `GroovyShell` in the test controller, and a deliberately broken file failed. Neither was run, so a misnamed step would not have been caught. The `?:` (Elvis) operator, `versions[-1]` (last list element) and `[:]` (an empty Map) in the two files are standard Groovy but not covered by the course's sources; check the Groovy documentation. The docs say the `library` step can load a library during the run [145], but this lesson did not test it.
:::

:::key-takeaways
- Bind secrets with `credentials()` or `withCredentials` and pass them to `sh` in single quotes. [143] [144]
- `parallel` for hand-written branches, `matrix` for combinations; `failFast` stops the rest. [143]
- Scripted is plain Groovy: `node`, `if`, `try`/`finally`, closures in a Map for `parallel`. [143] [144]
- A `vars/name.groovy` with `call()` becomes a step any Jenkinsfile can use after `@Library`. [145]
:::

:::glossary
- **Credential**: a secret stored in Jenkins and referred to by an id, never written into the Jenkinsfile.
- **GString**: a double-quoted Groovy string in which `${...}` is replaced before the string is used.
- **Interpolation**: replacing a placeholder in a string with a variable's value.
- **Matrix**: a stage that generates one parallel cell for every combination of the values on its axes.
- **Stash**: files saved during a run so a later stage on another agent can fetch them with `unstash`.
- **Scripted**: the older Jenkinsfile syntax that is plain Groovy, starting with `node { }`.
- **Closure**: a block of Groovy code in braces that can be stored in a variable and run later.
- **Groovy**: the programming language that Jenkinsfiles and shared libraries are written in.
- **Shared library**: a Git repository of reusable pipeline code that Jenkinsfiles load with `@Library`.
:::
