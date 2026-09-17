#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
PROJECT_DIR=$(realpath "${SCRIPT_DIR}/..")

export LD_LIBRARY_PATH="${PROJECT_DIR}/target/release${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"

# Rust emits libhelloworld_rust_binding.so. The test framework expects the same
# deployment filename as the packaged binding, so expose a local symlink.
ln -sfn "${PROJECT_DIR}/target/release/libhelloworld_rust_binding.so" \
    "${PROJECT_DIR}/target/release/helloworld-rust-binding.so"

python3 "${SCRIPT_DIR}/tests.py"
