# Walkthrough: Recover Graphviz Model Lineage with Terraform and Hugging Face

We have designed, implemented, and verified a new agent benchmark task named **Recover Graphviz Model Lineage with Terraform and Hugging Face**.

## Changes Made

We initialized the Snorkel task template inside `c:\snorkel` with the following files:

1. [task.toml](file:///c:/snorkel/task.toml): Configuration specifying metadata (author, medium difficulty, category, tags), resources (2 CPUs, 4GB RAM), verifier/agent timeouts, and `allow_internet = false`.
2. [instruction.md](file:///c:/snorkel/instruction.md): The user-facing instructions file specifying the metadata recovery requirements, the correct tree relationships for parent run ID reconstruction, the alphabetical key-sorted JSON formats for split label counts, and specific Graphviz DOT and SVG formatting requirements.
3. [Dockerfile](file:///c:/snorkel/environment/Dockerfile): Extends `python:3.12-slim-bookworm` to install tmux, asciinema, Graphviz, Terraform v1.9.0, required Python packages (pandas, datasets, huggingface_hub, pytest), and caches the `dair-ai/emotion` dataset during container build.
4. [corrupted_ledger.csv](file:///c:/snorkel/environment/corrupted_ledger.csv): The starter input CSV file with missing lineage attributes for the agent to recover.
5. [main.tf](file:///c:/snorkel/solution/main.tf): A reference Terraform module utilizing the built-in `terraform_data` resource to trigger `recover.py` via `local-exec` provisioner.
6. [recover.py](file:///c:/snorkel/solution/recover.py): Reference Python script that reads the corrupted CSV ledger, computes label counts offline from the pre-cached Hugging Face dataset, reconstructs the missing tree parentage and dataset revision attributes, outputs `recovered_ledger.csv` and `lineage.dot` with deterministic sorting (featuring customized node color fills by dataset split and modern Helvetica fonts), and compiles them into a Graphviz `lineage.svg` diagram.
7. [solve.sh](file:///c:/snorkel/solution/solve.sh): Script that runs the oracle solver.
8. [test.sh](file:///c:/snorkel/tests/test.sh): Verifier script that runs the test suite and outputs the final reward file.
9. [test_outputs.py](file:///c:/snorkel/tests/test_outputs.py): Test suite validating output format requirements, deterministic sorting, correct lineage parentage, accuracy mappings, and SVG validity.
10. [README.md](file:///c:/snorkel/README.md): Project overview, directory layout, setup instructions, and testing details.

---

## Verification Results

We verified the task by copying the files to the `/app` and `/tests` directories in a mock WSL environment (which replicates the agent sandbox) and running the solver and verifier:

- **Terraform Run**: Successfully applied the configuration in offline mode, pulling dataset splits from the local pre-cached directory and generating all three output artifacts.
- **Verifier Tests**: Executed the test suite using `pytest`. All 6 unit tests passed successfully.
- **Reward File**: The verifier script created a reward file containing `1`, indicating correct and complete task resolution.

```bash
============================== 6 passed in 0.09s ===============================
```
