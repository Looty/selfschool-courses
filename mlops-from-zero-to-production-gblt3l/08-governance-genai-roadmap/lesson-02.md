---
id: l30
title: "Accountability, documentation and security"
quiz: quiz-02.yaml
resources: []
sources: [1, 14, 16, 33, 47]
---
After this lesson you can list the records that make a model auditable, describe the approval points in a release path, and name two ML-specific attack types.

## Who can answer "why did it do that?"

When a model produces a harmful or surprising outcome, someone will ask which model version was live, how it was trained, on what data, who approved it and what the known limits were. If your pipeline keeps the records from the earlier chapters, you can answer. Here they are in one place.

| Question | Record | Lesson |
| --- | --- | --- |
| Which data? | Data version via a `.dvc` file in Git | 9 |
| Which code and parameters? | Run metadata: pipeline version, parameters, artifacts | 13, 15 |
| Which model was live? | Registry version and alias history | 14 |
| How was it tested? | Validation metrics, per-segment results, run metrics | 16 |
| Who approved it? | Preproduction approval and manual production step | 19 |
| What is it for, and where does it fail? | The model card | 15 |

Google's metadata list for a pipeline run includes the pipeline and component versions, parameters, pointers to artifacts, a pointer to the previous model and the evaluation metrics. [1] MLflow's packaging records the producing run and the environment files. [33] The model-card paper proposes documentation that accompanies a model and reports benchmarked performance across different conditions, including demographic, cultural and intersectional groups, the intended use contexts and the evaluation procedures. [16]

## Approval points

The pipeline's release path is where governance becomes enforceable. Google's guide has automatic deployment to a test environment, semi-automatic deployment to preproduction after reviewers approve a merge, and a manual production deployment after several successful preproduction runs. [1] CD4ML adds an orchestrator with manual governance gates and rollback support. [14] Decide who is allowed to approve what, and make the system record who did.

## Security: attacks that target ML

Ordinary application security applies to a model service. ML adds attacks on its inputs and its training data. The OWASP Machine Learning Security Top Ten (OWASP is a nonprofit that publishes lists of common security risks) includes **ML01 Input Manipulation Attack**, where attackers tweak the input slightly to trick the model (a sticker that makes a stop sign read as a speed limit), and **ML02 Data Poisoning Attack**, where they tamper with the training data so the model learns the wrong thing. [47]

The practical links back to this course: protect and version training data, since data is an axis of change (lessons 9, 10), validate inputs, and monitor prediction distributions for sudden shifts (lessons 26, 27). Restricting access to model outputs also reduces the problem of undeclared consumers described in the technical-debt paper. [47]

:::low-confidence
The OWASP project page says its content is a draft that is modified frequently, and it did not list all ten items when read for this course; only the names of ML01 and ML02 were confirmed. Read the current list directly before relying on it. The last sentence's link to undeclared consumers is the course's reasoning, not a claim of the OWASP page. [47]
:::

:::key-takeaways
- Keep records that answer which data, code, parameters, model version, tests, approver and documented limits. [1][16][33]
- Put approvals into the release path and record them. [1][14]
- Input manipulation and data poisoning are two named ML-specific attacks; protect data and inputs, and monitor predictions. [47]
:::

:::glossary
- **Accountability**: being able to say who decided what, and why.
- **Auditable**: its history can be checked after the fact.
- **Audit trail**: the records that let you reconstruct what happened.
- **Metadata**: records about runs, such as versions, parameters and results.
- **Lineage**: the chain from a live model back to its data and code.
- **Registry / alias history**: the log of which model version was live when.
- **Approval gate**: a required sign-off before moving to the next environment.
- **Preproduction**: the staging environment before production.
- **Model card**: documentation of a model's purpose, tests and limits.
- **Demographic / intersectional groups**: groups of people by traits, and by combinations of traits.
- **OWASP**: a nonprofit that lists the most common security risks.
- **Input manipulation attack**: crafting inputs to fool the model.
- **Data poisoning**: corrupting training data to change what the model learns.
- **Undeclared consumer**: an unknown system quietly using the model's output.
- **Axis of change**: one of the things that evolves (code, model, data) and needs versioning.
:::
