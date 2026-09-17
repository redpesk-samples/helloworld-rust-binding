# Build and installation

## Prerequisites

Two development setups can be used with this sample:

- the redpesk SDK container, which provides an isolated OCI-based development environment;
- a redpesk framework built and installed locally from sources.

For the container-based setup, see the [SDK container overview](https://docs.redpesk.bzh/docs/en/master/redpesk-os/sdk-container/docs/0-overview.html) and follow the [SDK container setup](https://docs.redpesk.bzh/docs/en/master/redpesk-os/sdk-container/docs/1-setup.html).

For a host installation, follow [Build framework on your computer](https://docs.redpesk.bzh/docs/en/master/redpesk-os/host-build/README.html) to build and install the AFB runtime and development environment from sources.

The sample additionally requires a Rust toolchain. For binder usage, see [Getting the binder](https://docs.redpesk.bzh/docs/en/master/redpesk-os/afb-binder/afb-getting.html).

The RPM specification declares the main build dependencies:

- Cargo and Rust;
- GCC;
- Clang development files;
- `json-c` development files;
- AFB Binding development files.

The `afbv4` dependency is resolved by Cargo from the `afb-librust` Git repository declared in `Cargo.toml` for normal source builds.

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

## Build the RPM package

RPM builds are handled by the redpesk factory tooling. The repository GitLab CI build job uses the official redpesk factory CI template and builds the package from `helloworld-rust-binding.spec`.

The same package can be built through a redpesk factory or a configured [redpesk local builder](https://docs.redpesk.bzh/docs/en/master/getting_started/local_builder_quickstart/docs/quickstart/0_quick-installation.html).

The RPM build uses the packaged Cargo vendor archive so that dependency resolution can run offline inside the build environment.

When using an RPM-based redpesk development environment, install the package build dependencies with:

```bash
dnf builddep helloworld-rust-binding
```

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
