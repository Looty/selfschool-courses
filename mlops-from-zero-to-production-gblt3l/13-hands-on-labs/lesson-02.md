---
id: l50
title: "Lab 2: version data and reproduce a pipeline with DVC"
quiz: quiz-02.yaml
resources: [../resources/lab2-make-data.py, ../resources/lab2-prepare.py, ../resources/lab2-train.py, ../resources/lab2-params.yaml, ../resources/lab2-dvc.yaml]
sources: [6, 37, 65]
---
After this lab you will have put a data file under DVC, pushed it to a remote, switched between two versions of it with Git, and described a two-stage pipeline in `dvc.yaml`.

This is a hands-on lab: do the steps on your own machine. The ready-made project files below were run in a test project while writing this course. The step-by-step commands come from the DVC get-started guide and the pipeline pages, which do not show every command's output, and were not all run verbatim. The lab takes longer than the estimate shown for it.

## Shortcut: ready-made project files

Download the five `lab2-*` files from this lesson's Resources. They replace the guide's sample download with a small made-up customer table, so nothing needs the internet, and the whole pipeline was run in a test project while writing this course. Lay them out like this:

```bash
mkdir dvc-lab && cd dvc-lab && mkdir src
# put lab2-make-data.py in the folder, and rename the others:
#   lab2-prepare.py -> src/prepare.py     lab2-train.py -> src/train.py
#   lab2-params.yaml -> params.yaml       lab2-dvc.yaml -> dvc.yaml
uv venv && uv pip install dvc scikit-learn pandas pyyaml
python lab2-make-data.py          # writes data/raw.csv
```

Use `data/raw.csv` wherever the steps below say `data/data.xml`, and `dvc repro` from step 5 runs the two stages. In a test, a second `dvc repro` skipped both stages, and changing `C` in `params.yaml` re-ran only the `train` stage. To make a second data version for step 4, delete 100 lines from `data/raw.csv`.

## Step 1: set up a repository

```bash
git init
dvc init
git commit -m "Initialize DVC"
```

Install DVC first with `uv tool install dvc` or `pipx install dvc`, and check with `dvc --help`. Initialising creates DVC's internal files, which you commit. [65]

## Step 2: track a data file

Download the guide's sample file, then track it. [65]

```bash
dvc get https://github.com/treeverse/dataset-registry get-started/data.xml -o data/data.xml
dvc add data/data.xml
git add data/data.xml.dvc data/.gitignore
git commit -m "Add raw data"
```

`dvc add` creates a small `data/data.xml.dvc` metadata file (a pointer saying which exact data version this is). The data itself goes into the DVC cache, a hidden local store, and is linked back into your working folder (the workspace). You commit the `.dvc` file and `data/.gitignore` to Git, not the data. [65] Open the `.dvc` file: it is the record Git versions in place of the data.

## Step 3: add a remote and push

```bash
dvc remote add -d myremote /tmp/dvcstore
dvc push
```

A local folder works as a remote for practice; the guide also shows S3, `dvc remote add -d storage s3://mybucket/dvcstore`. `dvc push` copies the cached data to the remote. After a `git pull` or `git clone`, `dvc pull` downloads it. [65]

## Step 4: change the data and switch versions

Modify the file (for example, delete a few lines), then record the change. [65]

```bash
dvc add data/data.xml
dvc push
git commit data/data.xml.dvc -m "Dataset updated"
```

Now go back: `git checkout HEAD~1 data/data.xml.dvc` selects the previous metadata, `dvc checkout` syncs the matching data into the workspace, and you commit the reverted `.dvc` file. A push is not needed, because the original version is already stored. [65] Check that your file is back to its original size.

## Step 5: a two-stage pipeline

A pipeline is declared in `dvc.yaml` as named stages with `cmd`, `deps`, `params` and `outs`. DVC builds the graph from dependencies and outputs. [6] A sketch for this lab (your scripts will differ):

```yaml
stages:
  prepare:
    cmd: python src/prepare.py
    deps: [src/prepare.py, data/data.xml]
    outs: [data/clean.csv]
  train:
    cmd: python src/train.py
    deps: [src/train.py, data/clean.csv]
    params: [learning_rate]
    outs: [models/model.pkl]
```

`dvc repro` restores the graph, works out which stages need to run and executes them in order; `--force` re-runs even when nothing changed. Without `--pull`, it does not run `dvc checkout` or `dvc pull`. [37] Run `dvc repro` twice: the second run should do nothing because no dependency changed. Then edit one parameter and see which stage runs.

## Check yourself

- After step 4, what is in Git and what is in the DVC cache?
- Why does reverting not need a `dvc push`?
- In step 5, which stage reruns when only `learning_rate` changes?

:::low-confidence
The get-started guide is a tutorial page; it does not explain remote configuration beyond the examples, and the stage definitions in step 5 are a sketch written for this lab, not a tested project. [65][6]
:::

:::key-takeaways
- `dvc add` tracks data and creates a `.dvc` file that Git versions; `dvc push` and `dvc pull` move data to and from the remote. [65]
- Switch data versions with `git checkout` of the `.dvc` file, then `dvc checkout`. [65]
- `dvc.yaml` stages declare `cmd`, `deps`, `params` and `outs`; `dvc repro` runs only what is needed. [6][37]
:::

:::glossary
- **DVC**: a tool that versions data files and pipelines alongside Git.
- **Repository (repo)**: a project folder tracked by Git.
- **`dvc init`**: set up DVC inside a Git repo.
- **`dvc get`**: download a file from another repo.
- **`dvc add`**: start tracking a data file with DVC.
- **`.dvc` file**: the small pointer file Git versions instead of the data.
- **Cache**: DVC's local store of data copies.
- **Workspace**: your current working folder.
- **Remote**: shared storage for the data (a folder, S3, ...).
- **`dvc push` / `dvc pull`**: upload data to / download data from the remote.
- **`dvc checkout`**: make the workspace match the `.dvc` files you currently have.
- **`HEAD~1`**: Git's name for "the commit before the current one".
- **`dvc.yaml`**: the file that defines a pipeline.
- **Stage**: one named step in the pipeline.
- **`cmd` / `deps` / `params` / `outs`**: the command, its inputs, its settings and its outputs.
- **`dvc repro`**: re-run only the stages whose inputs changed.
- **Parameter file**: a file of settings (like `learning_rate`) that stages read.
- **`uv` / `pipx`**: tools that install Python command-line programs.
:::
