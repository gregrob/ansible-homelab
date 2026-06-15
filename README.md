# ansible-homelab

<img src='docs/images/ansible-homelab.png' width='150'>

## Overview

`ansible-homelab` is a collection of Ansible playbooks and roles aimed at automating the setup and management of a personal homelab environment. The project focuses on provisioning infrastructure, deploying containerized applications, and ensuring consistent configurations across multiple systems.

## Notes
Housekeeping:
- `python3 vault-keys.py group_vars/all/vault.yaml` to generate a list of all the vault keys.

General container configuration (`user=root` as assumed `admin` user not setup yet):
- `ansible-playbook playbooks/configure-vm-debian-docker-network.yaml --ask-vault-pass` to configure static IP, DNS, and backbone interface with firewall rules (restarts networking — ensure Proxmox console access first).
- `ansible-playbook playbooks/configure-debian13-target.yaml --ask-vault-pass` to configure a Debian 13 VM or LXC for Docker operations. **This is the preferred playbook going forward** — set `is_lxc: true` (LXC) or `is_lxc: false` (VM) in the target's `host_vars` file, e.g.:
```yaml
  # host_vars/ollama-001.containers.max.lan.yaml
  is_lxc: true
```
- `ansible-playbook playbooks/configure-lxc-ansible-test.yaml --ask-vault-pass` to configure a lxc for ansible testing.
- `ansible-playbook playbooks/configure-lxc-ansible.yaml --ask-vault-pass` to configure a lxc for an ansible server.
- `ansible-playbook playbooks/configure-lxc-docker-privileged.yaml --ask-vault-pass` to configure a privileged lxc for docker operations. *(superseded by `configure-debian13-target.yaml`, kept for reference)*
- `ansible-playbook playbooks/configure-lxc-docker-unprivileged.yaml --ask-vault-pass` to configure an unprivileged lxc for docker operations. *(superseded by `configure-debian13-target.yaml`, kept for reference)*
- `ansible-playbook playbooks/configure-vm-debian-docker.yaml --ask-vault-pass` to configure a Debian VM for docker operations. *(superseded by `configure-debian13-target.yaml`, kept for reference)*
- `ansible-playbook playbooks/configure-rpi-nut.yaml --ask-vault-pass` to configure a Raspberry Pi for NUT (Network UPS Tools) server with web interface.

Targeted container configurations (`user=root` as assumed `admin` user not setup yet):
- `ansible-playbook playbooks/ansible-git.yaml --ask-vault-pass` to create a ansible github keys.
- `ansible-playbook playbooks/clone-git.yaml --ask-vault-pass` to clone git repositories.
- `ansible-playbook playbooks/configure-network-static.yaml --ask-vault-pass` to configure static IP addressing using NetworkManager (system will reboot to apply changes).
- `ansible-playbook playbooks/connect-secrets.yaml --ask-vault-pass` to connect to secrets server.
- `ansible-playbook playbooks/create-admin.yaml --ask-vault-pass` to create a admin user.

Jobs (`user=admin`):
- `ansible-playbook playbooks/apt-upgrade.yaml --ask-vault-pass` update and upgrade packages on Debian/Ubuntu systems.
- `ansible-playbook playbooks/disk-check.yaml --ask-vault-pass` checks the disk space of the host hasn't exceeded 80% and sends mail notification if it has.
- `ansible-playbook playbooks/fix-git-remotes.yaml --ask-vault-pass` fix corrupted Git remote URLs to proper SSH format.
- `ansible-playbook playbooks/git-pull-repos.yaml --ask-vault-pass` git pull on repos under `/srv`.
- `ansible-playbook playbooks/hello-world.yaml --ask-vault-pass` hello world test.
- `ansible-playbook playbooks/secrets-execute.yaml --ask-vault-pass` execute multiple commands on the secrets server for maintenance and monitoring.

## TODO

- ☐ Fix Docker log spammer - `fix_docker_log_spammer()`
- ☐ Network tuning for 10GbE
- ☐ Break out proper playbooks
- ☐ Remove superseded configure-lxc-docker-privileged/unprivileged and configure-vm-debian-docker playbooks once configure-debian13-target.yaml is proven

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.