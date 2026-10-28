<!--
SPDX-FileCopyrightText: 2026 DB Systel GmbH

SPDX-License-Identifier: CC-BY-4.0
-->

# Contributing to Compliance Assistant

Thank you for your interest in this project. Contributions are welcome. Feel free to open an issue with questions or reporting ideas and bugs before opening a pull request.

We are committed to fostering a welcoming, respectful, and harassment-free environment. Be kind!

## Secrets

Secrets live in `host_vars/` and `group_vars/` in files named `*.sops.yml`, encrypted with [SOPS](https://getsops.io) and [age](https://age-encryption.org). Each file can only be read by the age public keys listed for it in [`.sops.yaml`](.sops.yaml).

- Create your key with `age-keygen` and keep the private key in your SOPS `keys.txt` (or point `SOPS_AGE_KEY_FILE` to it). Send the public key (`age1…`) to a maintainer.
- Edit or create a secrets file with `sops host_vars/<host>.sops.yml`. Only secrets belong in these files, everything else goes into the plain vars files.
- After changing recipients in `.sops.yaml`, run `sops updatekeys <file>`. Rotate secrets of people who left, as they may have seen them.
- Requires `sops`, `age` and the `community.sops` Ansible collection.

## Contribution workflow

1. Fork the repository.
2. Create a new branch for your feature or bug fix: `git checkout -b feature-or-fix-name`
3. Make your changes and commit them with descriptive messages.
4. Push your changes to your forked repository: `git push origin feature-or-fix-name`
5. Open a Pull Request on the main repository.

It is assumed that you contribute under the [main license](LICENSE) of the project and own all the rights to the content you submit.
