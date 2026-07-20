import csv
import json
import os
import re
from pathlib import Path

OUTPUT_DIR = Path("/app/output")
EXPECTED_LEDGER_PATH = OUTPUT_DIR / "recovered_ledger.csv"
EXPECTED_DOT_PATH = OUTPUT_DIR / "lineage.dot"
EXPECTED_SVG_PATH = OUTPUT_DIR / "lineage.svg"

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

EXPECTED_LABEL_COUNTS = {
    "train": {"anger": 2159, "fear": 1937, "joy": 5362, "love": 1304, "sadness": 4666, "surprise": 572},
    "validation": {"anger": 275, "fear": 212, "joy": 704, "love": 178, "sadness": 550, "surprise": 81},
    "test": {"anger": 275, "fear": 224, "joy": 695, "love": 159, "sadness": 581, "surprise": 66}
}

EXPECTED_ACCURACY = {
    "run-001": "0.85",
    "run-002": "0.88",
    "run-003": "0.89",
    "run-004": "0.91",
    "run-005": "0.92",
    "run-006": "0.90",
    "run-007": "0.93",
    "run-008": "0.94"
}

EXPECTED_RUN_TYPES = {
    "run-001": "data_prep",
    "run-002": "model_train",
    "run-003": "model_train",
    "run-004": "hyperparameter_tuning",
    "run-005": "hyperparameter_tuning",
    "run-006": "model_train",
    "run-007": "model_distillation",
    "run-008": "model_eval"
}

def test_ledger_exists():
    """Verify that recovered_ledger.csv exists."""
    assert EXPECTED_LEDGER_PATH.is_file(), f"File not found: {EXPECTED_LEDGER_PATH}"

def test_ledger_content():
    """Verify recovered_ledger.csv columns, row count, sorting, and values."""
    assert EXPECTED_LEDGER_PATH.is_file()
    
    with open(EXPECTED_LEDGER_PATH, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # 1. Column presence check
    expected_fields = ["run_id", "parent_run_id", "run_type", "dataset_split", "label_counts", "dataset_revision", "accuracy"]
    assert reader.fieldnames == expected_fields, f"Columns mismatch: expected {expected_fields}, got {reader.fieldnames}"

    # 2. Row count check
    assert len(rows) == 8, f"Expected exactly 8 rows, got {len(rows)}"

    # 3. Deterministic sorting check (sorted by run_id)
    run_ids = [row["run_id"] for row in rows]
    expected_run_ids = sorted(list(LINEAGE.keys()))
    assert run_ids == expected_run_ids, f"Row ordering is not sorted by run_id: expected {expected_run_ids}, got {run_ids}"

    # 4. Values check for each row
    for row in rows:
        run_id = row["run_id"]
        
        # Check parent_run_id
        assert row["parent_run_id"] == LINEAGE[run_id], f"Parent mismatch for {run_id}: expected '{LINEAGE[run_id]}', got '{row['parent_run_id']}'"
        
        # Check run_type
        assert row["run_type"] == EXPECTED_RUN_TYPES[run_id], f"Run type mismatch for {run_id}: expected '{EXPECTED_RUN_TYPES[run_id]}', got '{row['run_type']}'"
        
        # Check dataset_revision
        assert row["dataset_revision"] == DATASET_REVISION, f"Dataset revision mismatch for {run_id}: expected '{DATASET_REVISION}', got '{row['dataset_revision']}'"
        
        # Check accuracy (comparing exact formatted strings)
        assert row["accuracy"] == EXPECTED_ACCURACY[run_id], f"Accuracy mismatch for {run_id}: expected {EXPECTED_ACCURACY[run_id]}, got {row['accuracy']}"
        
        # Check label_counts
        split_name = row["dataset_split"]
        expected_counts = EXPECTED_LABEL_COUNTS[split_name]
        try:
            parsed_counts = json.loads(row["label_counts"])
        except Exception as e:
            assert False, f"label_counts is not valid JSON for {run_id}: {row['label_counts']}"
            
        assert parsed_counts == expected_counts, f"Label counts mismatch for {run_id}: expected {expected_counts}, got {parsed_counts}"
        
        # Check sorting of keys in label_counts JSON string representation
        expected_json_str = json.dumps(expected_counts)
        assert row["label_counts"] == expected_json_str, f"JSON keys are not sorted alphabetically or spacing is incorrect: expected '{expected_json_str}', got '{row['label_counts']}'"

def test_dot_file_exists():
    """Verify that lineage.dot exists."""
    assert EXPECTED_DOT_PATH.is_file(), f"File not found: {EXPECTED_DOT_PATH}"

def test_dot_file_content():
    """Verify lineage.dot formatting, attributes, nodes, and edges."""
    assert EXPECTED_DOT_PATH.is_file()
    
    with open(EXPECTED_DOT_PATH, "r", encoding="utf-8") as f:
        dot_content = f.read()

    # 1. Check digraph definition
    assert re.search(r"digraph\s+G\s*\{", dot_content), "Must define directed graph G"

    # 2. Check dataset_revision graph-level attribute
    expected_revision_attr = f'dataset_revision="{DATASET_REVISION}";'
    assert expected_revision_attr in dot_content, f"Missing graph attribute: {expected_revision_attr}"

    # 3. Check node shape box styling
    expected_style = 'node [shape=box, style="filled,rounded", fontname="Helvetica", penwidth=1.5];'
    assert expected_style in dot_content, f"Missing or incorrect node styling block: {expected_style}"

    # 4. Check all node definitions and labels
    for run_id in LINEAGE.keys():
        run_type = EXPECTED_RUN_TYPES[run_id]
        acc = EXPECTED_ACCURACY[run_id]
        split_name = "train" if run_id in ["run-001", "run-002", "run-004", "run-007"] else ("validation" if run_id in ["run-003", "run-005"] else "test")
        counts_json_escaped = json.dumps(EXPECTED_LABEL_COUNTS[split_name]).replace('"', '\\"')
        
        expected_label = f"{run_id}\\n{run_type}\\n{acc}\\n{counts_json_escaped}"
        
        if split_name == "train":
            fillcolor = "#e1f5fe"
            color = "#0288d1"
        elif split_name == "validation":
            fillcolor = "#f3e5f5"
            color = "#7b1fa2"
        else: # test
            fillcolor = "#e8f5e9"
            color = "#388e3c"
            
        expected_node_def = f'"{run_id}" [label="{expected_label}", fillcolor="{fillcolor}", color="{color}"];'
        assert expected_node_def in dot_content, f"Missing or incorrect node definition: {expected_node_def}"

    # 5. Check all edges
    for child, parent in LINEAGE.items():
        if parent:
            expected_edge = f'"{parent}" -> "{child}";'
            assert expected_edge in dot_content, f"Missing or incorrect edge definition: {expected_edge}"

def test_svg_file_exists():
    """Verify that lineage.svg exists."""
    assert EXPECTED_SVG_PATH.is_file(), f"File not found: {EXPECTED_SVG_PATH}"

def test_svg_file_validity():
    """Verify that lineage.svg is a valid SVG document."""
    assert EXPECTED_SVG_PATH.is_file()
    
    with open(EXPECTED_SVG_PATH, "r", encoding="utf-8") as f:
        svg_content = f.read().strip()

    assert svg_content.startswith("<?xml") or svg_content.startswith("<svg"), "SVG file must start with xml declaration or svg tag"
    assert "</svg>" in svg_content, "SVG file must contain closing </svg> tag"
    
    # Check that it contains rendered node labels (hyphens are encoded as &#45; in Graphviz SVG labels)
    for run_id in LINEAGE.keys():
        expected_text = run_id.replace("-", "&#45;")
        assert expected_text in svg_content, f"SVG is missing text element for node {run_id} (expected text: {expected_text})"
