---
id: l09
title: Data versioning with DVC
quiz: quiz-01.yaml
resources: []
sources: [7, 14]
---
After this lesson you can version a dataset next to your code with DVC, and explain how a Git revision selects the matching data.

## The problem

Git is built for small text files, not for datasets of gigabytes. Yet a model is only as good as the data it learned from, and CD4ML treats data as one of three things that change, next to code and models. [14] If you cannot say which data produced a model, you cannot reproduce or audit it. DVC solves this by keeping the big data files outside Git and only a small "pointer" to each file inside Git.

DVC's own guide is clear about the design: "DVC is technically not a version control system by itself". Its small `.dvc` files define which data version applies, and Git versions those files. [7]

## The basic loop

The Get Started guide walks through these steps. [7]

```bash
git init
dvc init
git commit -m "Initialize DVC"

dvc add data/data.xml
git add data/data.xml.dvc data/.gitignore
git commit -m "Add raw data"
```

- `dvc init` creates internal files that you commit to Git.
- `dvc add` moves the file into the project cache (`.dvc/cache`), keyed by its hash, and links it back into the workspace. It writes `data/data.xml.dvc`, a small metadata file recording the hash. Git versions that file, and a `.gitignore` keeps the raw data out of Git.

## Remote storage

A **remote** is where DVC keeps copies of cached data. The guide uses a local directory and lists options such as Amazon S3, SSH, Google Drive and Azure Blob Storage. [7]

```bash
dvc remote add -d storage s3://mybucket/dvcstore
dvc push    # copy cached data to the remote
dvc pull    # fetch data from the remote
```

`dvc pull` is typically run after `git pull` or `git clone`, so teammates get the data that matches the checked-out code. [7]

## Changing and switching versions

When the data changes, re-add it, push it and commit the changed `.dvc` file. [7]

```bash
dvc add data/data.xml
dvc push
git commit data/data.xml.dvc -m "Dataset updates"
```

To go back, Git selects which `.dvc` revision you want and `dvc checkout` syncs the workspace to match. [7]

```bash
git checkout HEAD~1 data/data.xml.dvc
dvc checkout
```

No push is needed to go back, because the older version was already saved to the remote. [7]

## What this buys you

- A commit now identifies code **and** data. A model trained at a commit can be traced to its data.
- Data changes are reviewable like code changes, as a diff of the `.dvc` file.
- Branches can carry different data versions, which supports comparing experiments.

CD4ML notes that DVC can track file checksums so that a data change triggers a pipeline run just as a code commit does. It also lists data history, provenance and schema evolution as open challenges. [14] Versioning files is the first step; knowing that the data is valid, which comes next, is another.

:::key-takeaways
- Data is its own axis of change and needs versioning next to code. [14]
- DVC keeps data in a content-addressed cache and a remote, and Git versions the small `.dvc` files that point to it. [7]
- `dvc add`, `dvc push`, `dvc pull` and `dvc checkout` are the daily commands. [7]
:::

:::glossary
- **Dataset**: a collection of examples (rows of data) used to train or test a model.
- **DVC (Data Version Control)**: a tool that tracks big data files by storing a small pointer file in Git.
- **`.dvc` file**: the small text file that says which exact version of a data file to use.
- **Hash / checksum**: a fingerprint of a file's contents; the same contents always give the same fingerprint.
- **Cache**: a local folder where DVC keeps copies of data, named by their fingerprint.
- **Content-addressed**: stored and looked up by what the content is (its hash), not by file name.
- **Remote**: shared storage (S3, SSH, a drive) where DVC keeps the data copies for everyone.
- **S3 / Azure Blob**: Amazon's and Microsoft's cloud file storage.
- **Workspace**: your current working folder.
- **Revision**: one saved state in Git history, such as a commit.
- **Provenance**: the record of where something came from and how it was made.
- **Schema evolution**: the data's shape changing over time (new or renamed columns).
:::
