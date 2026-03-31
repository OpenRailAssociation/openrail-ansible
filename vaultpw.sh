#!/usr/bin/env sh

# Prepend common Homebrew/Linux binary paths to PATH
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

pw=$(gpg --batch --use-agent --decrypt ./vaultpw.gpg)

if [ -z "$pw" ]; then
  >&2 echo "Error: vaultpw.gpg is empty or decryption has failed"
  exit 1
else
  >&2 echo "vaultpw.gpg has been decrypted, resulting password is ${#pw} characters long"
  echo "$pw"
  exit 0
fi
