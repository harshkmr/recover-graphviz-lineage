# Recover Graphviz Model Lineage with Terraform and Hugging Face

You are tasked with recovering missing metadata in a corrupted CSV lineage ledger for an emotion-classifier model training sweep and generating Graphviz lineage visualization artifacts.

## Problem Description
A corrupted CSV ledger containing model sweep run logs is located at `/app/corrupted_ledger.csv`. It has missing values in the following fields for several runs:
1. `parent_run_id`: The parent run ID from which the model or dataset branched.
2. `label_counts`: A JSON representation summarizing the occurrences of each class label in the dataset split used for the training run.
3. `dataset_revision`: The git commit hash of the Hugging Face dataset `dair-ai/emotion` at that time.

You must build a reusable Terraform module in the root directory `/app` (or as a subdirectory module invoked by `/app/main.tf`) that performs the data recovery and outputs the recovered files.

The reusable module must act as the library interface. It must accept:
- `ledger_path` (string): Path to the input CSV ledger.
- `output_dir` (string): Path to the directory where the output artifacts should be written.

The module must execute a script (e.g., via Terraform's `local-exec` provisioner) to perform the metadata recovery and generate three outputs in the specified `output_dir`:
1. `recovered_ledger.csv`: A CSV file containing the fully reconstructed ledger.
2. `lineage.dot`: A Graphviz DOT format representation of the model lineage graph.
3. `lineage.svg`: An SVG image diagram rendered from `lineage.dot` using the `dot` command-line tool.

---

## Detailed Specifications

### 1. Recovery Logic

#### `parent_run_id`
The correct lineage tree relationships are documented in the audit report as follows:
- `run-001` is the root run and has no parent (empty string `""`).
- `run-002` and `run-003` are child runs of `run-001`.
- `run-004` and `run-005` are child runs of `run-002`.
- `run-006` and `run-007` are child runs of `run-003`.
- `run-008` is a child run of `run-007`.

#### `dataset_revision`
The dataset revision must be pinned to the exact commit hash:
`cab853a1dbdf4c42c2b3ef2173804746df8825fe`

#### `label_counts`
You must load/read the corresponding split of the Hugging Face dataset `dair-ai/emotion` (`train`, `validation`, or `test` as specified in `dataset_split`). Note that the environment runs **offline** (without internet access). The dataset has been pre-cached in the local environment and can be loaded offline.
For each run, calculate the frequency count of each string class label (`anger`, `fear`, `joy`, `love`, `sadness`, `surprise`) in that split.
Format the counts as a JSON string with keys sorted alphabetically (e.g., `{"anger": 2159, "fear": 1937, "joy": 5362, "love": 1304, "sadness": 4666, "surprise": 572}`).

---

### 2. Output File Formats

#### `recovered_ledger.csv`
- Must contain all columns: `run_id`, `parent_run_id`, `run_type`, `dataset_split`, `label_counts`, `dataset_revision`, `accuracy`.
- Rows must be sorted deterministically in lexicographical ascending order of `run_id` (e.g. `run-001`, `run-002`, ..., `run-008`).

#### `lineage.dot`
Must follow normalized Graphviz DOT formatting rules:
- Must define a directed graph `G` (`digraph G { ... }`).
- Must include a graph-level attribute: `dataset_revision="cab853a1dbdf4c42c2b3ef2173804746df8825fe";`
- Must specify node styling: `node [shape=box];`
- Every run in the ledger must be represented as a node named with its `run_id` quoted (e.g. `"run-001"`).
- Every node must have a `label` attribute containing the following four values, separated by literal newlines (`\n`):
  `run_id\nrun_type\naccuracy\nlabel_counts`
  (Example: `"run-001" [label="run-001\ndata_prep\n0.85\n{\"anger\": 2159, \"fear\": 1937, \"joy\": 5362, \"love\": 1304, \"sadness\": 4666, \"surprise\": 572}"];`)
- Directed edges must connect each parent run to its child run (e.g. `"run-001" -> "run-002";`), sorted alphabetically by child ID.

#### `lineage.svg`
- Must be generated from `lineage.dot` using the `dot` command-line tool.
- Must be a valid SVG file starting with `<?xml` or `<svg` and containing matching XML tags.

---

## Workspace Setup
The environment has:
- Terraform installed at `/usr/local/bin/terraform`.
- Python 3 with the Hugging Face `datasets` and `pandas` libraries installed.
- Graphviz CLI `dot` installed.
- The `dair-ai/emotion` Hugging Face dataset is pre-cached. Ensure you run your python commands or configuration with offline flags if necessary (e.g., setting the environment variables `HF_HUB_OFFLINE=1` and `HF_DATASETS_OFFLINE=1`).

To execute your solution, the verifier will run your Terraform module. Make sure to define the root module in `/app/main.tf` which sets up variable definitions and calls your module or performs the recovery, writing output files to the `output_dir` path variable.
