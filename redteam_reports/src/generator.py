import yaml
from pathlib import Path
from typing import Dict, List, Any


def parse_openapi_file(file_path: Path) -> Dict:
    """Parse the OpenAPI YAML file."""
    try:
        with open(file_path, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except yaml.YAMLError as e:
        raise ValueError(f"Failed to parse YAML: {e}")


def extract_schemas(openapi_data: Dict) -> List[Dict[str, Any]]:
    """Extract schemas from the OpenAPI specification."""
    return openapi_data.get("components", {}).get("schemas", {})


def classify_schemas(schemas: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Classify schemas into primary resources and filters/supporting types."""
    primary_resources = []

    for name, schema in schemas.items():
        # Check for Resource object criteria
        if schema.get("description", "").lower().startswith("a \"resource object\""):
            attributes = schema.get("properties", {}).get("attributes", {}).get("properties", {})
            primary_resources.append({
                "name": name,
                "attributes": [
                    {"name": attr_name, **attr_details}
                    for attr_name, attr_details in attributes.items()
                ],
                "required": schema.get("required", []),
            })

    return primary_resources


def build_mix_command(resource: Dict[str, Any]) -> List[str]:
    """Generate a `mix` command for the given resource."""
    attributes = resource["attributes"]
    attr_parts = []

    for attr in attributes:
        attr_name = attr["name"]
        attr_type = attr.get("type", "string")
        modifiers = []
        if attr_name in resource["required"]:
            modifiers.append("required")
        attr_parts.append(f"{attr_name}:{attr_type}:{':'.join(modifiers)}" if modifiers else f"{attr_name}:{attr_type}")

    attr_str = ",".join(attr_parts)
    return ["mix", "gen_ash.resource", resource["name"], f"--attribute {attr_str}"]


def main(openapi_file_path: Path, execute: bool = False):
    """Main function to parse OpenAPI file and generate mix commands."""
    print("==== Testing OpenAPI Utility Functions ====")

    # Step 1: Parse OpenAPI file
    print("\nStep 1: Parsing OpenAPI file")
    try:
        openapi_data = parse_openapi_file(openapi_file_path)
        print(f"Successfully parsed OpenAPI file: {openapi_file_path}")
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        return

    # Step 2: Extract and classify schemas
    print("\nStep 2: Extracting resources")
    schemas = extract_schemas(openapi_data)
    primary_resources = classify_schemas(schemas)

    if not primary_resources:
        print("No primary resources found in the OpenAPI specification.")
        return

    print(f"Found {len(primary_resources)} primary resources:")
    for resource in primary_resources:
        print(f"- {resource['name']}")

    # Step 3: Describe resources and attributes
    print("\nStep 3: Describing primary resources and attributes")
    for resource in primary_resources:
        print(f"\nResource: {resource['name']}")
        for attr in resource["attributes"]:
            required = " (required)" if attr["name"] in resource["required"] else ""
            print(f"- {attr['name']}: {attr.get('type', 'string')}{required}")

    # Step 4: Generate mix commands
    print("\nStep 4: Generating `mix` commands for primary resources")
    for resource in primary_resources:
        command = build_mix_command(resource)
        print(f"Generated command for resource '{resource['name']}': {' '.join(command)}")
        if execute:
            print(f"Executing command for resource '{resource['name']}'...")
            # Mock execution
            print(f"Mock execution: {' '.join(command)}")

    print("\n==== Testing Complete ====")


if __name__ == "__main__":
    # import sys

    openapi_file = Path("openapi2.yaml")
    # execute_commands = "--execute" in sys.argv
    main(openapi_file, execute=False)
