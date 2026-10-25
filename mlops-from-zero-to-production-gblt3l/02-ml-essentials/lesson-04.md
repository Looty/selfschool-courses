---
id: l08
title: Reproducibility
quiz: quiz-04.yaml
resources: []
sources: [2, 5, 7, 27, 30]
---
After this lesson you can list what must be recorded to reproduce a training run, set the main seeds, and say what you still cannot reproduce.

## Why it is harder than "pin the dependencies"

For ordinary software, the same code and the same inputs give the same output. For ML, results also depend on the data, random seeds (the starting numbers behind "random" choices), hardware and library versions. The technical-debt paper names reproducibility debt: randomised algorithms, nondeterminism in parallel learning and dependence on initial conditions make strict reproducibility hard. [2] PyTorch's notes are blunt about the limit: completely reproducible results are not guaranteed across PyTorch releases, individual commits or platforms, and CPU and GPU runs may differ even with identical seeds. [30]

So the aim is practical: make runs repeatable where you can, and record enough to explain differences where you cannot.

## Control the randomness

PyTorch lists the main controls. [30]

- `torch.manual_seed(0)` seeds the random number generator for CPU and CUDA, and some operations use random numbers internally, so set it at the start of the application.
- `random.seed(0)` seeds Python's generator, which may be needed for custom operators.
- `np.random.seed(0)` seeds NumPy's global generator; NumPy `Generator` objects must be seeded separately.
- `torch.use_deterministic_algorithms()` makes PyTorch use deterministic implementations where available and raises an error for known nondeterministic operations that have no deterministic alternative.
- `torch.backends.cudnn.deterministic = True` makes the selected cuDNN algorithm deterministic. `torch.backends.cudnn.benchmark = False` makes the algorithm choice deterministic, possibly at a performance cost; setting it to `True` can improve speed when run-to-run reproducibility is not needed.
- For data loading, DataLoader reseeds its workers; to keep runs reproducible pass a `worker_init_fn` and a `generator` seeded with `manual_seed()`.

scikit-learn has its own rules through `random_state`. An integer gives the same result on every call to `fit` or `split`; `None` or a `RandomState` instance gives different results each call. Its recommendation for reproducibility is to remove all uses of `random_state=None` and create one `RandomState` at the top of the program and pass it to every randomised object. [27]

## Record what the seed cannot

Seeds fix randomness. Reproducing a run also needs the inputs and the settings.

- **Data version.** DVC records a hash of a data file in a small `.dvc` file that Git versions, so a Git revision selects the data version, and `dvc checkout` restores the matching data. [7]
- **Parameters, metrics and artifacts.** MLflow Tracking records a run's parameters, metrics, start and end times, and output files such as model weights, and ties each to an experiment, so runs can be compared and found again. [5]
- **Code.** The commit that produced the run belongs in the same record.
- **Environment.** Library versions and hardware type matter, given the limits above.

A useful test is to ask: could a colleague reproduce this model next quarter from the record alone? If the answer needs a conversation, something is missing.

:::low-confidence
How much run-to-run variation remains after seeding depends on the framework, the hardware and the operations used. PyTorch's notes say determinism is not guaranteed across releases or platforms. Treat bit-for-bit reproduction as a goal for debugging and compare metrics within a tolerance otherwise. [30]
:::

:::key-takeaways
- Reproducibility is hard because of randomness, parallelism, hardware and library versions; it is not guaranteed across PyTorch releases or platforms. [2][30]
- Seed Python, NumPy and the framework; use deterministic-algorithm settings where needed. [30]
- Record data version, code, parameters, metrics and artifacts together. [5][7]
:::

:::glossary
- **Reproducibility**: being able to get the same result again from the same record.
- **Random seed**: the starting number of a random number generator; same seed, same "random" sequence.
- **Nondeterministic**: may give different results each run even with the same input.
- **CUDA / cuDNN**: NVIDIA's toolkit and deep-learning library for running maths on GPUs.
- **GPU**: a graphics chip that is very good at the parallel maths models need.
- **Deterministic algorithm**: one that always gives the same output for the same input.
- **DataLoader / worker**: PyTorch's helper that loads data in parallel background processes.
- **`random_state`**: scikit-learn's name for a seed setting.
- **DVC**: a tool that versions big data files alongside Git.
- **Hash**: a short fingerprint of a file; any change to the file changes it.
- **MLflow Tracking**: a tool that logs each training run's settings, scores and files.
- **Parameters**: settings you chose for a run (or numbers a model learned, depending on context).
- **Artifact**: a file a run produces, such as the model.
- **Weights**: the learned numbers inside a model.
- **Tolerance**: how big a difference you accept as "the same".
:::
