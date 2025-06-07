#!/usr/bin/env python3
import subprocess
import sys
import yaml
import os

def get_vault_content(vault_file):
    try:
        result = subprocess.run(
            ['ansible-vault', 'view', vault_file],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error decrypting vault file: {e.stderr}", file=sys.stderr)
        sys.exit(1)

def extract_keys_as_dict(yaml_content):
    try:
        data = yaml.safe_load(yaml_content)
        if isinstance(data, dict):
            # Create dict with keys and empty string values
            return {key: "" for key in data.keys()}
        else:
            print("Vault content is not a dictionary.", file=sys.stderr)
            sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}", file=sys.stderr)
        sys.exit(1)

def save_keys_to_file(keys_dict, vault_file):
    # Prepare output filename in same dir as vault_file
    vault_dir = os.path.dirname(os.path.abspath(vault_file))
    vault_base = os.path.splitext(os.path.basename(vault_file))[0]
    output_file = os.path.join(vault_dir, f"{vault_base}_keys.yaml")

    try:
        with open(output_file, 'w') as f:
            yaml.dump(keys_dict, f, default_flow_style=False)
        print(f"Keys saved to {output_file}")
    except Exception as e:
        print(f"Failed to save keys file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} vault_file", file=sys.stderr)
        sys.exit(1)

    vault_file = sys.argv[1]
    content = get_vault_content(vault_file)
    keys_dict = extract_keys_as_dict(content)

    print("Extracted keys:")
    for key in keys_dict.keys():
        print(key)

    save_keys_to_file(keys_dict, vault_file)
