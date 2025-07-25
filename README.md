# ansible-homelab

<img src='docs/images/ansible-homelab.png' width='150'>

## Overview

`ansible-homelab` is a collection of Ansible playbooks and roles aimed at automating the setup and management of a personal homelab environment. The project focuses on provisioning infrastructure, deploying containerized applications, and ensuring consistent configurations across multiple systems.

## Notes
Housekeeping:
- `python3 vault-keys.py group_vars/all/vault.yaml` to generate a list of all the vault keys.

Container configuration:
- `ansible-playbook playbooks/configure-lxc-ansible.yaml --ask-vault-pass` to configure a lxc for an ansible server.
- `ansible-playbook playbooks/configure-lxc.yaml --ask-vault-pass` to configure a generic lxc.
- `ansible-playbook playbooks/create-admin.yaml --ask-vault-pass` to create a admin user.
- `ansible-playbook playbooks/ansible-git.yaml --ask-vault-pass` to create a ansible github keys.

Jobs:
- `ansible-playbook playbooks/hello-world.yaml --ask-vault-pass` hello world test.
- `ansible-playbook playbooks/git-pull-repos.yaml --ask-vault-pass` git pull on repos under `/srv`.

## TODO

- ☐ Fix Docker log spammer - `fix_docker_log_spammer()`
- ☐ Network tuning for 10GbE
- ☐ Break out proper playbooks

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
