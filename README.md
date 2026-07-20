# Recover Graphviz Model Lineage with Terraform and Hugging Face

This benchmark task tests an agent's ability to use Terraform and Python offline to recover corrupted training sweep metadata, query label counts from a pre-cached Hugging Face dataset, and generate Graphviz lineage visualization artifacts.

---

## Directory Structure

- `task.toml`: Task metadata, CPU/Memory configurations, and time limits.
- `instruction.md`: The detailed user-facing prompt outlining task requirements, the audit report lineage structure, and output specifications.
- `environment/`
  - `Dockerfile`: Environment build file. Installs Terraform, Graphviz, required Python libraries, and pre-caches the `dair-ai/emotion` dataset.
  - `corrupted_ledger.csv`: The starter input CSV file containing missing data fields.
- `solution/`
  - `main.tf`: Reference Terraform root module implementing the `terraform_data` recovery resource.
  - `recover.py`: The Python recovery script that queries dataset split label counts, reconstructs parent relationships, and outputs the recovered ledger and DOT/SVG lineage graphs.
  - `solve.sh`: The reference shell script that executes the Terraform apply.
- `tests/`
  - `test.sh`: The verifier entry point script that invokes `pytest` and creates the reward file.
  - `test_outputs.py`: Automated unit tests verifying outputs (CSV sorting and counts, DOT hierarchy/styles, SVG validity).

---

## Getting Started

### Prerequisites
- **Docker**: For sandboxing and building the container environment.
- **WSL (Ubuntu) / Linux**: If you wish to run the scripts directly outside of Docker.

### Local Development / Testing (WSL)

To test the solution manually inside WSL, you can run the following sequence:

1. **Copy Files to Mock Sandbox Paths**:
   ```bash
   mkdir -p /app /tests
   cp /mnt/c/snorkel/environment/corrupted_ledger.csv /app/corrupted_ledger.csv
   cp -r /mnt/c/snorkel/solution/* /app/
   cp -r /mnt/c/snorkel/tests/* /tests/
   ```

2. **Execute the Solver Script**:
   ```bash
   bash /app/solve.sh
   ```
   This will run `terraform init` and `terraform apply`, saving the recovered files (`recovered_ledger.csv`, `lineage.dot`, `lineage.svg`) to `/app/output/`.

3. **Run the Verification Suite**:
   ```bash
   bash /tests/test.sh
   ```
   This will execute the `pytest` unit tests. If successful, `/logs/verifier/reward.txt` will be created with content `1`.

---

## Recovered Graph Styling

The generated `lineage.svg` renders runs using modern, color-coded node styling with Helvetica font settings:
- **Train Split (Light Blue)**: `#e1f5fe` fill, `#0288d1` border.
- **Validation Split (Light Purple)**: `#f3e5f5` fill, `#7b1fa2` border.
- **Test Split (Light Green)**: `#e8f5e9` fill, `#388e3c` border.
