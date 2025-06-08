# ansible-homelab

<img src='docs/images/ansible-homelab.png' width='150'>

## Overview

`ansible-homelab` is a collection of Ansible playbooks and roles aimed at automating the setup and management of a personal homelab environment. The project focuses on provisioning infrastructure, deploying containerized applications, and ensuring consistent configurations across multiple systems.

## Notes

- `python3 vault-keys.py group_vars/all/vault.yaml` to generate a list of all the vault keys.
- `ansible-playbook playbooks/configure-lxc.yaml --ask-vault-pass` to configure a lxc.
- `ansible-playbook playbooks/create-admin.yaml --ask-vault-pass` to create a admin user.
- `ansible-playbook playbooks/ansible-git.yaml --ask-vault-pass` to create a ansible github keys.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
