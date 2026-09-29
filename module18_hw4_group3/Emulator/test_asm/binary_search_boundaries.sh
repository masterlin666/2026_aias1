#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
for spec in "2:0" "47:11" "30:-1"; do
    val="${spec%%:*}"
    exp="${spec##*:}"
  cp test_asm/binary_search.asm /tmp/bs.asm
  sed -i "s/\.word 23/.word ${val}/" /tmp/bs.asm
  result=$(./obj/emulator /tmp/bs.asm -s 2>&1 | awk '/x15:/{print $1}')
  echo "search=${val} expected=${exp} got ${result}"
done
