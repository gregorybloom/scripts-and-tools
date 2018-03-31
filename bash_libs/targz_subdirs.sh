#!/bin/bash
IFS=$'\n'

tardirs() {
  targetdir="$1"

  curdir="$PWD"
  cd "$targetdir"
  for dir in */; do
    tar -cvzf "${dir::-1}.tar.gz" "$dir";
  done
  for dir in */; do
    sudo rm -Rvf "$dir";
  done
  cd "$curdir"
}
