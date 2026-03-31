# Ansible Inventory

A TOML-based inventory (`inventory.toml`) of all hosts managed with Ansible. The
Python script [`generate_inventory`](generate_inventory) parses this file and
outputs group-based JSON for Ansible to consume as a dynamic inventory.

## How it works

The script [`generate_inventory`](generate_inventory) recursively finds an
`inventory.toml` file, reads it, and constructs a well-defined Ansible dynamic
inventory JSON. This allows for streamlined adding, removing, and changing of
hosts and their groups.

### Inventory format

`inventory.toml` uses a simple TOML structure where each key is a hostname and
the value is a list of groups it belongs to:

```toml
example1.openrailassociation.org = ["servers", "web"]
example2.openrailassociation.org = ["servers", "db"]
```

Hostnames with dots can be quoted or unquoted — the script handles both.

### Usage

The script supports the standard Ansible dynamic inventory interface:

- `./generate_inventory --list` — outputs the full inventory as JSON
- `./generate_inventory --host <hostname>` — returns an empty dict (host
  variables are not stored here)

### Example output

Given the inventory above, `./generate_inventory --list` would output:

```json
{
  "_meta": {
    "hostvars": {}
  },
  "servers": {
    "hosts": [
      "example1.openrailassociation.org",
      "example2.openrailassociation.org"
    ]
  },
  "web": {
    "hosts": [
      "example1.openrailassociation.org"
    ]
  },
  "db": {
    "hosts": [
      "example2.openrailassociation.org"
    ]
  }
}
```

## Resources

- [Ansible Docs on working with inventories](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html)
- [Ansible Docs on working with dynamic inventories](https://docs.ansible.com/ansible/latest/user_guide/intro_dynamic_inventory.html)
