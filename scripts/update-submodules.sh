#!/bin/sh

# check if given submodule has a newer tag upstream
#
# ideally, renovate-bot should be able to do this on its own, but alas
# it only tracks commits:
# https://github.com/renovatebot/renovate/discussions/24890

set -e

# Get all submodule paths
submodules=$(git config --file .gitmodules --get-regexp path | awk '{ print $2 }')

for submodule in $submodules; do
  echo "----------------------------------------------"
  printf "checking submodule %s\n" "$submodule"

  # get submodule URL
  submodule_url=$(cd "$submodule" && git config --get remote.origin.url)
  printf "submodule URL: %s\n" "$submodule_url"

  # fetch commit id recorded for the submodule
  old_head=$(git -C "$submodule"/ rev-list HEAD --max-count=1)
  old_tag=$(git -C "$submodule"/ describe --tags "$old_head" 2>/dev/null || echo "no tag")
  old_tag_date=$(git -C "$submodule"/ log -1 --format=%as "$old_head")

  # fetch and identify latest tag
  git -C "$submodule"/ fetch
  latest_tag_ref=$(git -C "$submodule"/ rev-list --tags --max-count=1)
  if [ -z "$latest_tag_ref" ]; then
    printf "no tags found in submodule %s\n" "$submodule"
    continue
  fi
  latest_tag=$(git  -C "$submodule"/ describe --tags "$latest_tag_ref")
  latest_tag_date=$(git -C "$submodule"/ log -1 --format=%as "$latest_tag_ref")

  if [ "$old_head" = "$latest_tag_ref" ]; then
    printf "no newer tag than %s (%s)\n" "$old_tag" "$old_tag_date"
  else
    printf "submodule HEAD: %s\n" "$old_head"
    printf "submodule tag: %s (%s)\n" "$old_tag" "$old_tag_date"
    printf "latest tag ref: %s\n" "$latest_tag_ref"
    printf "latest tag: %s (%s)\n" "$latest_tag" "$latest_tag_date"
    # upgrade instructions
    magic_command="git -C $submodule checkout $latest_tag && git c \"submodules: update $submodule to $latest_tag\" $submodule"
    printf "not running the latest, update submodule with \n\n%s\n" "$magic_command"
  fi

done
