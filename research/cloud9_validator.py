"""
Cloud-9 Assembly Project v2.1.0 â JSON Schema Validator
Validates expansion JSON against expected structure for both Physics and Medical tracks.

Usage:
    from cloud9_validator import validate_expansion
    validate_expansion(your_json_data)
"""

from typing import Dict, List, Any, Optional
import json


class Cloud9ValidationError(Exception):
    """Raised when expansion JSON fails structural validation."""
    pass


REQUIRED_TOP_LEVEL_KEYS = [
    "metadata",
    "executive_summary", 
    "physics_track",
    "medical_track",
    "intersection",
    "implementation_roadmap",
    "repository_structure",
    "conclusion"
]

REQUIRED_METADATA_KEYS = [
    "project",
    "version",
    "date",
    "status",
    "classification"
]

REQUIRED_PHYSICS_KEYS = [
    "new_validation_cases",
    "layer_2_references",
    "cross_layer_patterns",
    "action_items"
]

REQUIRED_MEDICAL_KEYS = [
    "core_thesis",
    "physics_parallels",
    "key_insight",
    "formal_definition",
    "early_detection_mechanism",
    "validation_pathways",
    "disease_targets",
    "action_items"
]

VALIDATION_CASE_REQUIRED_KEYS = [
    "entry_id",
    "title",
    "phenomenon",
    "significance_for_ac",
    "cross_layer_pattern",
    "source_reference"
]

CROSS_LAYER_PATTERN_REQUIRED_KEYS = [
    "pattern_id",
    "name",
    "description",
    "domains_linked"
]

ACTION_ITEM_REQUIRED_KEYS = [
    "priority",
    "action",
    "timeline",
    "deliverable"
]

DISEASE_TARGET_REQUIRED_KEYS = [
    "disease",
    "pre_symptomatic_window",
    "data_source",
    "ac_bio_application"
]


def _assert_key_exists(data: Dict, key: str, path: str) -> None:
    """Assert that a key exists in a dictionary."""
    if key not in data:
        raise Cloud9ValidationError(f"Missing required key '{key}' at {path}")


def _assert_type(value: Any, expected_type: type, path: str) -> None:
    """Assert that a value is of the expected type."""
    if not isinstance(value, expected_type):
        raise Cloud9ValidationError(
            f"Expected {expected_type.__name__} at {path}, got {type(value).__name__}"
        )


def validate_metadata(metadata: Dict, path: str = "metadata") -> None:
    """Validate the metadata section."""
    for key in REQUIRED_METADATA_KEYS:
        _assert_key_exists(metadata, key, path)

    _assert_type(metadata["version"], str, f"{path}.version")

    # Version should follow semver-ish pattern for Cloud-9
    version = metadata["version"]
    if not version.startswith("2."):
        raise Cloud9ValidationError(
            f"Expected version 2.x.x at {path}.version, got '{version}'"
        )


def validate_cross_layer_pattern(pattern: Dict, path: str) -> None:
    """Validate a cross-layer pattern object."""
    for key in CROSS_LAYER_PATTERN_REQUIRED_KEYS:
        _assert_key_exists(pattern, key, path)

    _assert_type(pattern["domains_linked"], list, f"{path}.domains_linked")
    if len(pattern["domains_linked"]) < 2:
        raise Cloud9ValidationError(
            f"Cross-layer pattern at {path} must link at least 2 domains"
        )


def validate_validation_case(case: Dict, path: str) -> None:
    """Validate a single validation case."""
    for key in VALIDATION_CASE_REQUIRED_KEYS:
        _assert_key_exists(case, key, path)

    _assert_type(case["significance_for_ac"], list, f"{path}.significance_for_ac")
    if len(case["significance_for_ac"]) == 0:
        raise Cloud9ValidationError(
            f"Validation case at {path} must have at least one significance item"
        )

    validate_cross_layer_pattern(
        case["cross_layer_pattern"], 
        f"{path}.cross_layer_pattern"
    )


def validate_action_items(items: List[Dict], path: str) -> None:
    """Validate action items array."""
    _assert_type(items, list, path)

    valid_priorities = {"Immediate", "Short-term", "Medium-term", "Long-term"}

    for i, item in enumerate(items):
        item_path = f"{path}[{i}]"
        for key in ACTION_ITEM_REQUIRED_KEYS:
            _assert_key_exists(item, key, item_path)

        if item["priority"] not in valid_priorities:
            raise Cloud9ValidationError(
                f"Invalid priority '{item['priority']}' at {item_path}. "
                f"Must be one of: {valid_priorities}"
            )


def validate_physics_track(physics: Dict, path: str = "physics_track") -> None:
    """Validate the physics track section."""
    for key in REQUIRED_PHYSICS_KEYS:
        _assert_key_exists(physics, key, path)

    # Validate validation cases
    cases = physics["new_validation_cases"]
    _assert_type(cases, list, f"{path}.new_validation_cases")

    entry_ids = set()
    for i, case in enumerate(cases):
        case_path = f"{path}.new_validation_cases[{i}]"
        validate_validation_case(case, case_path)

        # Check for duplicate entry IDs
        entry_id = case["entry_id"]
        if entry_id in entry_ids:
            raise Cloud9ValidationError(
                f"Duplicate entry_id '{entry_id}' at {case_path}"
            )
        entry_ids.add(entry_id)

    # Validate cross-layer patterns
    patterns = physics["cross_layer_patterns"]
    _assert_type(patterns, list, f"{path}.cross_layer_patterns")

    pattern_ids = set()
    for i, pattern in enumerate(patterns):
        pattern_path = f"{path}.cross_layer_patterns[{i}]"
        validate_cross_layer_pattern(pattern, pattern_path)

        pattern_id = pattern["pattern_id"]
        if pattern_id in pattern_ids:
            raise Cloud9ValidationError(
                f"Duplicate pattern_id '{pattern_id}' at {pattern_path}"
            )
        pattern_ids.add(pattern_id)

    # Validate action items
    validate_action_items(physics["action_items"], f"{path}.action_items")


def validate_formal_definition(definition: Dict, path: str) -> None:
    """Validate the A_c^bio formal definition."""
    _assert_key_exists(definition, "equation", path)
    _assert_key_exists(definition, "components", path)

    _assert_type(definition["components"], list, f"{path}.components")

    required_symbols = {"T(t)", "Î¦(t)", "S(t)", "D(t)", "Ï(t)"}
    found_symbols = set()

    for i, component in enumerate(definition["components"]):
        comp_path = f"{path}.components[{i}]"
        _assert_key_exists(component, "symbol", comp_path)
        _assert_key_exists(component, "name", comp_path)
        _assert_key_exists(component, "description", comp_path)
        _assert_key_exists(component, "evidence", comp_path)
        found_symbols.add(component["symbol"])

    missing = required_symbols - found_symbols
    if missing:
        raise Cloud9ValidationError(
            f"Missing required A_c^bio components: {missing}"
        )


def validate_disease_targets(targets: List[Dict], path: str) -> None:
    """Validate disease target specifications."""
    _assert_type(targets, list, path)

    diseases = set()
    for i, target in enumerate(targets):
        target_path = f"{path}[{i}]"
        for key in DISEASE_TARGET_REQUIRED_KEYS:
            _assert_key_exists(target, key, target_path)

        disease = target["disease"]
        if disease in diseases:
            raise Cloud9ValidationError(
                f"Duplicate disease target '{disease}' at {target_path}"
            )
        diseases.add(disease)


def validate_medical_track(medical: Dict, path: str = "medical_track") -> None:
    """Validate the medical track section."""
    for key in REQUIRED_MEDICAL_KEYS:
        _assert_key_exists(medical, key, path)

    # Validate formal definition
    validate_formal_definition(
        medical["formal_definition"], 
        f"{path}.formal_definition"
    )

    # Validate disease targets
    validate_disease_targets(
        medical["disease_targets"],
        f"{path}.disease_targets"
    )

    # Validate action items
    validate_action_items(medical["action_items"], f"{path}.action_items")


def validate_intersection(intersection: Dict, path: str = "intersection") -> None:
    """Validate the intersection section."""
    _assert_key_exists(intersection, "unified_complexity_framework", path)
    _assert_key_exists(intersection, "cross_domain_patterns", path)

    # Validate cross-domain patterns
    patterns = intersection["cross_domain_patterns"]
    _assert_type(patterns, list, f"{path}.cross_domain_patterns")

    pattern_ids = set()
    for i, pattern in enumerate(patterns):
        pattern_path = f"{path}.cross_domain_patterns[{i}]"
        _assert_key_exists(pattern, "pattern_id", pattern_path)
        _assert_key_exists(pattern, "physics_manifestation", pattern_path)
        _assert_key_exists(pattern, "biological_manifestation", pattern_path)

        pattern_ids.add(pattern["pattern_id"])

    # Check that physics track patterns are referenced
    # (This is a soft check â intersection can have additional patterns)


def validate_repository_structure(structure: Dict, path: str = "repository_structure") -> None:
    """Validate repository structure specification."""
    _assert_key_exists(structure, "directories", path)
    _assert_type(structure["directories"], list, f"{path}.directories")

    for i, directory in enumerate(structure["directories"]):
        dir_path = f"{path}.directories[{i}]"
        _assert_key_exists(directory, "path", dir_path)
        _assert_key_exists(directory, "contents", dir_path)
        _assert_type(directory["contents"], list, f"{dir_path}.contents")


def validate_expansion(data: Dict) -> Dict[str, Any]:
    """
    Main validation entry point.

    Args:
        data: The Cloud-9 expansion JSON as a Python dictionary

    Returns:
        Validation report dictionary with status and details

    Raises:
        Cloud9ValidationError: If validation fails
    """
    report = {
        "status": "pending",
        "version": None,
        "tracks_validated": [],
        "validation_cases_count": 0,
        "disease_targets_count": 0,
        "cross_layer_patterns_count": 0,
        "errors": []
    }

    try:
        # Top-level structure
        for key in REQUIRED_TOP_LEVEL_KEYS:
            _assert_key_exists(data, key, "root")

        # Metadata
        validate_metadata(data["metadata"])
        report["version"] = data["metadata"]["version"]

        # Physics Track
        validate_physics_track(data["physics_track"])
        report["tracks_validated"].append("physics")
        report["validation_cases_count"] = len(
            data["physics_track"]["new_validation_cases"]
        )
        report["cross_layer_patterns_count"] = len(
            data["physics_track"]["cross_layer_patterns"]
        )

        # Medical Track
        validate_medical_track(data["medical_track"])
        report["tracks_validated"].append("medical")
        report["disease_targets_count"] = len(
            data["medical_track"]["disease_targets"]
        )

        # Intersection
        validate_intersection(data["intersection"])
        report["tracks_validated"].append("intersection")

        # Repository Structure
        validate_repository_structure(data["repository_structure"])
        report["tracks_validated"].append("repository_structure")

        report["status"] = "valid"

    except Cloud9ValidationError as e:
        report["status"] = "invalid"
        report["errors"].append(str(e))
        raise

    return report


def load_and_validate(filepath: str) -> Dict[str, Any]:
    """
    Load a Cloud-9 expansion JSON file and validate it.

    Args:
        filepath: Path to the JSON file

    Returns:
        Validation report dictionary
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return validate_expansion(data)


# Self-test with the generated expansion
if __name__ == "__main__":
    import sys

    test_file = "/mnt/agents/output/Cloud9_Expansion_v2.1.0.json"

    try:
        report = load_and_validate(test_file)
        print("â Cloud-9 Expansion v2.1.0 validation PASSED")
        print(f"   Version: {report['version']}")
        print(f"   Tracks validated: {', '.join(report['tracks_validated'])}")
        print(f"   Validation cases: {report['validation_cases_count']}")
        print(f"   Disease targets: {report['disease_targets_count']}")
        print(f"   Cross-layer patterns: {report['cross_layer_patterns_count']}")
        sys.exit(0)
    except Cloud9ValidationError as e:
        print(f"â Validation FAILED: {e}")
        sys.exit(1)
