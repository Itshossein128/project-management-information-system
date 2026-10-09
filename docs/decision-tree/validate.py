#!/usr/bin/env python3
"""Read-only structural and registered-route validation for this decision tree.

Run from any directory: python3 /path/to/docs/decision-tree/validate.py
Uses the standard library; does not import the application or require services.
"""

from __future__ import annotations

import json
import re
import sys
from collections import deque
from pathlib import Path
from urllib.parse import unquote, urlsplit


TREE = Path(__file__).resolve().parent
REPO = TREE.parent.parent
SECTIONS = (
    "Context & Screen",
    "Action Taken",
    "Authorization & Permissions",
    "Desired Result",
    "Outcomes & Guards",
    "Subsequent Decisions",
    "Source Evidence",
)
FIELDS = (
    "Route", "Component", "Initial State", "Trigger", "Inputs",
    "Required Permissions", "Required Roles / Groups",
    "API Call", "State Change", "Navigation", "UI Feedback",
)


def registered_routes(repo: Path) -> dict[str, tuple[str, str]]:
    """Resolve the explicit route calls used by this repository's route config.

    Fail closed if config syntax changes instead of silently omitting a route.
    Layouts have no URL and are not counted as registered screens.
    """
    app = repo / "apps/web/src/app"
    variables = (app / "routeVars.ts").read_text(encoding="utf-8")
    components, segments = variables.split("export const PATHS =", 1)
    constants = re.compile(r'^\s*(\w+):\s*"([^"]+)"', re.MULTILINE)
    paths = dict(constants.findall(segments))
    files = dict(constants.findall(components))
    result: dict[str, tuple[str, str]] = {}
    pattern = re.compile(
        r'\broute\(\s*(`[^`]+`|PATHS\.\w+|"[^"]+")\s*,\s*ROUTES\.(\w+)'
    )
    for config in ("routes.ts", "routes/business-setup.routes.ts"):
        text = (app / config).read_text(encoding="utf-8")
        # Comments should not count as live route declarations.
        text = re.sub(r"/\*.*?\*/|//[^\n]*", "", text, flags=re.DOTALL)
        matches = pattern.findall(text)
        expected = len(re.findall(r"\broute\s*\(", text))
        if len(matches) != expected:
            raise ValueError(f"{config}: unsupported route syntax; review the validator")
        for expression, key in matches:
            value = expression.strip('`"')
            value = re.sub(
                r"\$\{PATHS\.(?:BUSINESS_DEPT\.)?(\w+)\}",
                lambda match: paths[match[1]],
                value,
            )
            if value.startswith("PATHS."):
                value = paths[value.split(".")[-1]]
            if "${" in value:
                raise ValueError(f"Unresolved route expression: {expression}")
            if key in result:
                raise ValueError(f"Route component {key} is reused: review inventory schema")
            result[key] = ("/" + value, "apps/web/src/app/" + files[key])
    root_config = (app / "routes.ts").read_text(encoding="utf-8")
    if len(re.findall(r"\bindex\(ROUTES\.INDEX\)", root_config)) != 1:
        raise ValueError("Expected one INDEX route; review the validator")
    result["INDEX"] = ("/", "apps/web/src/app/" + files["INDEX"])
    return result


def route_problems(inventory: dict, routes: dict, nodes: set[str]) -> list[str]:
    problems = []
    listed = {}
    for item in inventory["routes"]:
        key = item["key"]
        if key in listed:
            problems.append(f"Duplicate inventory route key: {key}")
        listed[key] = item
        if item["node"] not in nodes:
            problems.append(f"{key}: missing decision node {item['node']}")
        if key in routes and (item["path"], item["source"]) != routes[key]:
            problems.append(f"{key}: URL/component differs from current route config")
    for key in routes.keys() - listed.keys():
        problems.append(f"Undocumented registered route: {key} {routes[key][0]}")
    for key in listed.keys() - routes.keys():
        problems.append(f"Inventory route no longer registered: {key}")
    if len({item["path"] for item in inventory["routes"]}) != len(listed):
        problems.append("Duplicate URL patterns in inventory")
    return problems


def validate(repo: Path = REPO, tree: Path = TREE) -> tuple[list[str], dict[str, int]]:
    problems = []
    inventory = json.loads((tree / "inventory.json").read_text(encoding="utf-8"))
    if inventory.get("schema_version") != 1:
        raise ValueError("Unsupported inventory schema_version")
    manifest = {item["path"]: item for item in inventory["nodes"]}
    if len(manifest) != len(inventory["nodes"]):
        problems.append("Duplicate decision node in inventory")
    documents = {
        str(path.parent.relative_to(tree)): path
        for path in tree.rglob("README.md") if path.parent != tree
    }
    for missing in manifest.keys() - documents.keys():
        problems.append(f"Missing decision README: {missing}")
    for extra in documents.keys() - manifest.keys():
        problems.append(f"Unindexed decision README: {extra}")
    for directory in tree.rglob("*"):
        if directory.is_dir() and directory.name != "__pycache__":
            if not (directory / "README.md").is_file():
                problems.append(f"Directory has no README: {directory.relative_to(tree)}")
    routes = registered_routes(repo)
    problems.extend(route_problems(inventory, routes, set(documents)))
    graph: dict[str, set[str]] = {key: set() for key in documents}
    link_count = 0
    source_count = 0
    for key, document in {**documents, ".": tree / "README.md"}.items():
        text = document.read_text(encoding="utf-8")
        if key != ".":
            for segment in Path(key).parts:
                if not re.fullmatch(r"(?:[a-z0-9]+(?:-[a-z0-9]+)*|\[[a-z0-9]+(?:-[a-z0-9]+)*\])", segment):
                    problems.append(f"Invalid decision directory name: {key}")
            if not text.startswith("# Decision: "):
                problems.append(f"Missing decision title: {key}")
            for section in SECTIONS:
                if f"## {section}\n" not in text:
                    problems.append(f"{key}: missing section {section}")
            for field in FIELDS:
                if not re.search(rf"\*\*{re.escape(field)}\*\*:\s*\S", text):
                    problems.append(f"{key}: missing/empty field {field}")
            if key in manifest:
                bracketed = Path(key).name.startswith("[")
                if bracketed != manifest[key]["protected"]:
                    problems.append(f"{key}: protected notation differs from inventory")
            if re.search(r"\b(?:TODO|TBD|FIXME)\b", text):
                problems.append(f"{key}: unresolved documentation marker")
        targets = set()
        for raw in re.findall(r"\]\(([^\n)]+)\)", text):
            url = urlsplit(raw.strip("<>"))
            if url.scheme or url.netloc or not url.path:
                continue
            if "[" in url.path or "]" in url.path:
                problems.append(f"{key}: bracketed link is not URL encoded: {raw}")
            target = (document.parent / unquote(url.path)).resolve()
            if target.is_dir():
                target /= "README.md"
            link_count += 1
            if not target.is_file():
                problems.append(f"{key}: broken link {raw}")
                continue
            if not target.is_relative_to(repo.resolve()):
                problems.append(f"{key}: local link escapes repository: {raw}")
            targets.add(target)
            if target.is_relative_to(tree.resolve()) and target.name == "README.md":
                destination = str(target.parent.relative_to(tree.resolve()))
                if key in graph and destination in graph:
                    graph[key].add(destination)
        if key != ".":
            sources = text.split("## Source Evidence\n", 1)[-1]
            if not re.search(r"\]\((?:\.\./)+apps/", sources):
                problems.append(f"{key}: missing linked application source evidence")
            else:
                source_count += 1
            for child in document.parent.iterdir():
                if child.is_dir() and (child / "README.md").is_file():
                    if (child / "README.md").resolve() not in targets:
                        problems.append(f"{key}: child not linked: {child.name}")
    visited = set()
    pending = deque(["login"])
    while pending:
        current = pending.popleft()
        if current in visited:
            continue
        visited.add(current)
        pending.extend(graph.get(current, set()) - visited)
    for unreachable in set(documents) - visited:
        problems.append(f"Unreachable from login: {unreachable}")
    return problems, {
        "decisions": len(documents), "routes": len(routes),
        "local_links": link_count, "source_backed_nodes": source_count,
        "reachable_nodes": len(visited & set(documents)),
    }


def main() -> int:
    try:
        problems, counts = validate()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Decision tree validation failed: {error}", file=sys.stderr)
        return 1
    if problems:
        print("Decision tree validation failed:", file=sys.stderr)
        for problem in sorted(set(problems)):
            print(f"- {problem}", file=sys.stderr)
        return 1
    print(
        f"Decision tree valid: {counts['decisions']} decisions, "
        f"{counts['routes']} registered routes, {counts['local_links']} local links; "
        f"all nodes reachable and source-backed."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
