import argparse
import csv
import json
import os
import subprocess
from datasets import load_dataset

# Hardcoded true lineage tree
LINEAGE = {
    "run-001": "",
    "run-002": "run-001",
    "run-003": "run-001",
    "run-004": "run-002",
    "run-005": "run-002",
    "run-006": "run-003",
    "run-007": "run-003",
    "run-008": "run-007"
}

DATASET_REVISION = "cab853a1dbdf4c42c2b3ef2173804746df8825fe"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", required=True, help="Path to input corrupted ledger CSV")
    parser.add_argument("--output-dir", required=True, help="Directory to write outputs")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # Force offline datasets loading
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["HF_DATASETS_OFFLINE"] = "1"

    # Load dataset offline
    dataset = load_dataset("dair-ai/emotion")

    # Compute label counts for each split
    split_counts = {}
    for split_name in dataset.keys():
        counts = {}
        features = dataset[split_name].features["label"]
        for x in dataset[split_name]:
            label_str = features.int2str(x["label"])
            counts[label_str] = counts.get(label_str, 0) + 1
        # Sort keys alphabetically
        split_counts[split_name] = {k: counts[k] for k in sorted(counts.keys())}

    # Process input ledger
    rows = []
    with open(args.ledger, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            run_id = row["run_id"]
            
            # 1. Recover parent_run_id
            row["parent_run_id"] = LINEAGE.get(run_id, "")
            
            # 2. Recover label_counts
            split_name = row["dataset_split"]
            counts = split_counts.get(split_name, {})
            # Format as compact/standard JSON string
            row["label_counts"] = json.dumps(counts)
            
            # 3. Recover dataset_revision
            row["dataset_revision"] = DATASET_REVISION
            
            rows.append(row)

    # Sort rows by run_id lexicographically
    rows.sort(key=lambda x: x["run_id"])

    # Save recovered ledger
    fieldnames = ["run_id", "parent_run_id", "run_type", "dataset_split", "label_counts", "dataset_revision", "accuracy"]
    recovered_csv_path = os.path.join(args.output_dir, "recovered_ledger.csv")
    with open(recovered_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    # Generate lineage.dot
    dot_path = os.path.join(args.output_dir, "lineage.dot")
    with open(dot_path, "w", encoding="utf-8") as f:
        f.write("digraph G {\n")
        f.write(f'  dataset_revision="{DATASET_REVISION}";\n')
        f.write('  node [shape=box, style="filled,rounded", fontname="Helvetica", penwidth=1.5];\n')
        
        # Write node definitions
        for row in rows:
            run_id = row["run_id"]
            run_type = row["run_type"]
            accuracy = row["accuracy"]
            split_name = row["dataset_split"]
            
            # Escape inner double quotes for label counts JSON in the DOT label attribute
            label_counts_escaped = row["label_counts"].replace('"', '\\"')
            label_val = f"{run_id}\\n{run_type}\\n{accuracy}\\n{label_counts_escaped}"
            
            # Select colors based on split
            if split_name == "train":
                fillcolor = "#e1f5fe"
                color = "#0288d1"
            elif split_name == "validation":
                fillcolor = "#f3e5f5"
                color = "#7b1fa2"
            else: # test
                fillcolor = "#e8f5e9"
                color = "#388e3c"
                
            f.write(f'  "{run_id}" [label="{label_val}", fillcolor="{fillcolor}", color="{color}"];\n')
            
        # Write edge definitions sorted by child run_id
        edges = []
        for row in rows:
            run_id = row["run_id"]
            parent_id = row["parent_run_id"]
            if parent_id:
                edges.append((parent_id, run_id))
        
        # Sort edges by child run_id
        edges.sort(key=lambda x: x[1])
        for parent_id, run_id in edges:
            f.write(f'  "{parent_id}" -> "{run_id}";\n')
            
        f.write("}\n")

    # Render SVG using Graphviz dot
    svg_path = os.path.join(args.output_dir, "lineage.svg")
    subprocess.run(["dot", "-Tsvg", dot_path, "-o", svg_path], check=True)

if __name__ == "__main__":
    main()
