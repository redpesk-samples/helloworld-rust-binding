# Build and installation

## Prerequisites

The recommended development environment is the redpesk SDK, which provides the AFB development stack and the packages required to build bindings.

For more information, see [Setup your build host](https://docs.redpesk.bzh/docs/en/master/getting_started/host-configuration/docs/1-Setup-your-build-host.html) and [Getting the binder](https://docs.redpesk.bzh/docs/en/master/redpesk-os/afb-binder/afb-getting.html) in the official redpesk documentation.

The RPM specification declares the main build dependencies:

- Cargo and Rust;
- GCC;
- Clang development files;
- `json-c` development files;
- AFB Binding development files.

When the redpesk source repositories are configured, the RPM build dependencies can be installed with:

```bash
dnf builddep helloworld-rust-binding
```

The `afbv4` dependency is resolved by Cargo from the `afb-librust` Git repository declared in `Cargo.toml`.

## Install from packages

On a system configured with the appropriate redpesk repositories, install the binding with:

```bash
dnf install helloworld-rust-binding
```

The packaged application is installed under:

```text
/usr/redpesk/helloworld-rust-binding/
```

The shared library is located at:

```text
/usr/redpesk/helloworld-rust-binding/lib/helloworld-rust-binding.so
```

To verify the installed files, run:

```bash
rpm -ql helloworld-rust-binding
```

For package deployment on a redpesk target, refer to the [redpesk application deployment documentation](https://docs.redpesk.bzh/docs/en/master/getting_started/docs/deployment.html).

## Build from sources

Clone the project:

```bash
git clone https://github.com/redpesk-samples/helloworld-rust-binding.git
cd helloworld-rust-binding
```

The recommended repository helper builds the release library and creates the deployment-name symlink expected by the local examples and tests:

```bash
make build
```

Cargo produces:

```text
target/release/libhelloworld_rust_binding.so
```

and the Makefile creates:

```text
target/release/helloworld-rust-binding.so -> libhelloworld_rust_binding.so
```

The symlink is useful because Cargo follows Rust library naming rules while the redpesk package and the functional tests use the deployment name `helloworld-rust-binding.so`.

## Build directly with Cargo

The equivalent Cargo build is:

```bash
cargo build --release --package helloworld-rust-binding
```

When building directly with Cargo, create the local deployment-name symlink before using the commands documented for the source tree:

```bash
ln -sfn libhelloworld_rust_binding.so \
    target/release/helloworld-rust-binding.so
```

## Format the Rust source

The repository provides a formatting helper:

```bash
make fmt
```

It runs `cargo fmt` for the `helloworld-rust-binding` package.

## Clean the build

Remove Cargo build artifacts with:

```bash
make clean
```
