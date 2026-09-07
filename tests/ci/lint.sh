#!/usr/bin/env bash
set -euo pipefail

command -v cargo >/dev/null 2>&1 || sudo dnf install -y cargo rust rustfmt
cargo fmt --package helloworld-rust-binding -- --check
