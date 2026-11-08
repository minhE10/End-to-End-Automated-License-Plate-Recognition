"""Validate planning artifacts only. Does not certify dataset/model acceptance gates."""
from __future__ import annotations

import ast
import csv
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote

try:
    import yaml
    from jsonschema import Draft202012Validator
except ImportError as exc:
    raise SystemExit(f"Missing docs dependency: {exc}. Install requirements-docs.txt")

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/plan"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def reject_constant(value: str):
    raise ValueError(f"Nonfinite JSON constant: {value}")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"),
                      parse_constant=reject_constant, object_pairs_hook=unique_object)


class UniqueSafeLoader(yaml.SafeLoader):
    pass


def yaml_mapping(loader, node):
    loader.flatten_mapping(node)
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        require(key not in result, f"Duplicate YAML key: {key}")
        result[key] = loader.construct_object(value_node)
    return result


UniqueSafeLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, yaml_mapping)


def check_links():
    count = 0
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        require("\ufffd" not in text, f"Replacement character in {path}")
        for match in re.finditer(r"!?\[[^\]]*\]\(([^\n)]+)\)", text):
            target = match.group(1).strip().strip("<>")
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
                continue
            local = unquote(target.split("#", 1)[0])
            resolved = (path.parent / local).resolve()
            require(resolved.is_relative_to(ROOT), f"Local link escapes repo: {path}: {target}")
            require(resolved.exists(), f"Broken local link: {path}: {target}")
            count += 1
    return count


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, strict=True)
        records = list(reader)
    require(bool(records), f"Empty CSV: {path}")
    header, *rows = records
    require(len(set(header)) == len(header), f"Duplicate CSV columns: {path}")
    require(all(len(row) == len(header) for row in rows), f"Ragged CSV: {path}")
    return [dict(zip(header, row)) for row in rows]


def check_schema(contract, documents):
    Draft202012Validator.check_schema(contract)
    templates = {
        "source-manifest.example.json": "SourceManifest",
        "data-manifest.example.json": "DataManifest",
        "model-manifest.example.json": "ModelManifest",
        "run-manifest.example.json": "RunManifest",
        "release-manifest.example.json": "ReleaseManifest",
        "charset.example.json": "Charset",
    }
    for filename, kind in templates.items():
        document = documents[PLAN / "templates" / filename]
        schema = {"$schema": contract["$schema"], "$defs": contract["$defs"],
                  "$ref": f"#/$defs/{kind}"}
        validator = Draft202012Validator(schema)
        validator.validate(document)
        Draft202012Validator(contract).validate(document)
        if kind != "Charset":
            require(document["status"] == "TEMPLATE_NOT_A_RELEASE", f"Template claims release: {filename}")
            incomplete_ready = {**document, "status": "READY"}
            require(not validator.is_valid(incomplete_ready), f"Incomplete READY accepted: {kind}")
    # Verify that constraints are meaningful, not just a syntactically valid schema.
    charset = documents[PLAN / "templates/charset.example.json"]
    bad_charset = {**charset, "blank_index": 9}
    require(not Draft202012Validator({"$defs": contract["$defs"], "$ref": "#/$defs/Charset"}).is_valid(bad_charset),
            "Invalid blank index accepted")
    return len(templates)


def check_benchmarks(benchmarks, csv_rows):
    records = benchmarks["benchmarks"]
    ids = [record["id"] for record in records]
    require(len(set(ids)) == len(ids), "Duplicate benchmark IDs")
    require([row["id"] for row in csv_rows] == ids, "Benchmark CSV IDs/order mismatch")
    required = ["id", "gate", "owner", "name", "formula", "direction", "dataset", "split",
                "denominator", "aggregation", "minimum", "stretch", "unit", "kind", "rationale",
                "resource_assumption", "confidence", "evidence", "planned_command", "command_status"]
    main_md = (PLAN / "05-weekly-goals-and-benchmarks.md").read_text(encoding="utf-8")
    weeks = sorted(PLAN.glob("0[1-4]-week-*.md"))
    for record, row in zip(records, csv_rows):
        require(all(key in record and record[key] != "" for key in required), f"Incomplete {record['id']}")
        gate_index = int(record["gate"][1])
        require(record["id"].startswith(record["gate"] + "."), "Gate/id mismatch")
        require(record["owner"] == "ABCD"[gate_index - 1], "Benchmark ownership mismatch")
        require(record["observed"] is None and record["observed_n"] is None
                and record["status"] == "CHƯA ĐO", "Fabricated benchmark observation")
        require(row["observed"] == row["observed_n"] == "null" and row["status"] == "CHƯA ĐO",
                "CSV observation must stay unmeasured")
        for key in ["gate", "owner", "split", "unit"]:
            require(row[key] == record[key], f"CSV field mismatch {record['id']}.{key}")
        require(json.loads(row["minimum"]) == record["minimum"], "CSV threshold mismatch")
        require(record["command_status"] == "PLANNED_NOT_IMPLEMENTED", "Future command status mismatch")
        require("--benchmark " + record["id"] in record["planned_command"], "Missing per-ID command")
        threshold = ("bắt buộc báo số đo" if record["minimum"] is None else
                     f"{record['direction']} {record['minimum']} {record['unit']}")
        expected = f"| {record['id']} | {record['name']} | {threshold} | {record['kind']} |"
        weekly = weeks[gate_index - 1].read_text(encoding="utf-8")
        require(expected in main_md and expected in weekly, f"Markdown benchmark table mismatch {record['id']}")
        require(f"### {record['id']} —" in main_md, f"Missing benchmark detail {record['id']}")
        for detail in [record["formula"], record["denominator"], record["rationale"],
                       record["resource_assumption"], record["evidence"], record["planned_command"]]:
            require(detail in main_md, f"Benchmark detail mismatch {record['id']}: {detail}")
    return len(records)


def check_budget(backlog, benchmarks):
    for week in benchmarks["weeks"]:
        owner = week["owner"]
        rows = [row for row in backlog if row["owner"] == owner]
        require(all(int(row["week"]) == week["week"] and row["gate"] == week["gate"] for row in rows),
                f"Owner/week/gate mismatch {owner}")
        actual = sum(int(row["hours"]) for row in rows if row["kind"] == "SUGGESTED")
        reserve = sum(int(row["hours"]) for row in rows if row["kind"] == "RESERVE")
        require(actual == week["work_hours"] == 34 and reserve == week["reserve_hours"] == 6,
                f"Budget mismatch {owner}")
        if owner != "A":
            require(int(rows[0]["hours"]) == week["receiver_check_hours"] == 2, f"Missing 2h receiving {owner}")
        weekly_file = next(PLAN.glob(f"0{week['week']}-week-*.md"))
        text = weekly_file.read_text(encoding="utf-8")
        for row in rows:
            if row["kind"] == "SUGGESTED":
                require(f"| {row['id']} | {row['task']} | {row['hours']} |" in text, f"Task mismatch {row['id']}")


def check_config(config, contract, benchmarks, documents):
    require(config["seed"] == 42, "Seed mismatch")
    for k in ["plan_version", "contract_version", "protocol_version"]:
        require(config[k] == benchmarks[k], f"Version mismatch {k}")
    require(contract["x-contract-version"] == benchmarks["contract_version"], "Contract version mismatch")
    require(config["data"]["target"] == benchmarks["split_sizes"]["target"], "Target counts mismatch")
    require(config["data"]["minimum"] == benchmarks["split_sizes"]["minimum"], "Minimum counts mismatch")
    require(config["data"]["split_before_crop"] and not config["data"]["test_gold_runtime_access"], "Data isolation mismatch")
    ctc = contract["x-ctc"]
    recognizer = config["recognizer"]
    require(recognizer["input_shape"] == [1, 32, 160] and recognizer["output_timesteps"] == ctc["time_steps"] == 40,
            "CTC shape/time mismatch")
    charset = documents[PLAN / "templates/charset.example.json"]
    tokens = charset["tokens"]
    payload = (json.dumps(tokens, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()
    require(digest == charset["tokens_sha256"] == ctc["charset_sha256"] == recognizer["charset_tokens_sha256"],
            "Charset hash mismatch")
    require(len(tokens) == ctc["num_classes"] == recognizer["num_classes"] == 68, "Charset/head mismatch")
    require(tokens[0] == "<CTC_BLANK>" and charset["blank_index"] == recognizer["blank_index"] == 0,
            "CTC blank mismatch")
    require("O" not in tokens and len(set(tokens)) == len(tokens), "Sentinel/duplicate charset token")
    require(recognizer["components"] == ["CNN", "BiLSTM", "CTCLoss"] and recognizer["decoder"] == "greedy-ctc-v1",
            "Required architecture/decoder mismatch")
    require(config["crop"]["rectification"] == "none", "Baseline must not use oracle rectification")
    require(config["evaluation"]["include_failed_images"] and config["evaluation"]["misses_as_empty_for_pipeline_cer"],
            "Full-split denominator policy mismatch")
    # Every normative field must have a matching generated Markdown row.
    md = (PLAN / "06-data-contract-and-handoffs.md").read_text(encoding="utf-8")
    for name, definition in contract["$defs"].items():
        require(f"### {name}\n" in md, f"Missing Markdown schema {name}")
        section = md.split(f"### {name}\n", 1)[1].split("\n### ", 1)[0].split("\n## ", 1)[0]
        for field in definition["properties"]:
            require(f"| `{field}` |" in section, f"Missing Markdown field {name}.{field}")


def check_runtime_boundary():
    path = ROOT / "src/alpr/interfaces.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    classes = {node.name: node for node in tree.body if isinstance(node, ast.ClassDef)}
    for name, expected in [("RuntimeImage", {"sample_id", "pixels"}),
                           ("RuntimeCrop", {"crop_id", "sample_id", "pixels"})]:
        fields = {node.target.id for node in classes[name].body if isinstance(node, ast.AnnAssign)}
        require(fields == expected, f"Ground-truth/path field entered runtime interface {name}")
    for name, method in [("Detector", "detect"), ("Recognizer", "recognize"),
                         ("Pipeline", "predict"), ("Evaluator", "evaluate")]:
        require(any(isinstance(node, ast.FunctionDef) and node.name == method for node in classes[name].body),
                f"Missing interface {name}.{method}")


def main():
    documents = {path: read_json(path) for path in ROOT.rglob("*.json") if ".git" not in path.parts}
    config_files = list(ROOT.rglob("*.yaml"))
    configs = {path: yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueSafeLoader) for path in config_files}
    csv_files = {path: read_csv(path) for path in ROOT.rglob("*.csv")}
    contract = documents[PLAN / "data-contract.json"]
    benchmarks = documents[PLAN / "weekly-benchmarks.json"]
    templates = check_schema(contract, documents)
    count = check_benchmarks(benchmarks, csv_files[PLAN / "benchmark-results-template.csv"])
    check_budget(csv_files[PLAN / "recommended-backlog.csv"], benchmarks)
    config = configs[PLAN / "config/recommended-implementation.example.yaml"]
    check_config(config, contract, benchmarks, documents)
    check_runtime_boundary()
    for row in csv_files[PLAN / "templates/experiment-results-template.csv"]:
        require(row["status"] == "CHƯA ĐO", "Experiment must be unmeasured")
        require(all(row[key] == "null" for key in ["n_images", "n_gt_chars", "coverage", "cer_micro", "exact_accuracy", "e2e_accuracy"]),
                "Fabricated experiment metric")
    py_count = 0
    for path in ROOT.rglob("*.py"):
        if ".git" not in path.parts:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            py_count += 1
    links = check_links()
    print(f"PASS: {len(documents)} JSON, {len(configs)} YAML, {len(csv_files)} CSV, "
          f"{templates} schema templates, {count} benchmarks, {links} local links, {py_count} Python files.")
    print("PASS: schema/ownership/versions/charset/CTC, Markdown-JSON-CSV agreement; 4 x(34+6)=160 hours.")
    print("Scope: planning validation only. Dataset/model gates remain CHƯA ĐO.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
