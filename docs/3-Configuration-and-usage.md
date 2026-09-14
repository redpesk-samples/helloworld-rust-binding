# Configuration and usage

## Runtime configuration

`helloworld-rust-binding` does not require an application-specific runtime configuration file. For source-tree development, it is a loadable AFB V4 binding configured through the `afb-binder` command line.

For the complete binder command-line interface, refer to the [`afb-binder` manual](https://docs.redpesk.bzh/docs/en/master/redpesk-os/afb-binder/afb-binder.1.html).

When installed as a redpesk package, `manifest.yml` describes the packaged service and declares the `helloworld` API to the redpesk application framework. It is stored as `rpconfig/manifest.yml` in the sources and installed as `.rpconfig/manifest.yml` in the application directory.

## Run a source build

After `make build`, start `afb-binder` and load the binding from the Cargo release directory:

```bash
afb-binder -vvv -b ./target/release/helloworld-rust-binding.so
```

Unless another port is configured, the binder listens on port `1234`.

## Run the installed service

Start the packaged redpesk application through the application framework:

```bash
afm-util start helloworld-rust-binding
```

Loading the installed shared library directly with `afb-binder` can be useful for development or debugging, but it bypasses the normal application-framework startup path and should not be used as the standard packaged-service workflow.

## Call the API

When the source build is started manually with `afb-binder` on the default port, use `afb-client` from another terminal:

```bash
afb-client -H localhost:1234/api helloworld hello
```

A packaged application started through `afm-util` may expose the API through a transport selected by the application framework, such as a Unix socket, so do not assume that `localhost:1234` is available in that mode. Use the endpoint provided by the application configuration.

Calls to the application verbs also publish the `helloworld/verb_called` event. See the [API reference](./4-Api-reference.html) for the complete verb, request, reply and event contract.

## Running on a redpesk target

The same RPM can be installed on a compatible redpesk target. Target provisioning and package deployment are platform-level operations and are intentionally not duplicated here:

- [Application deployment](https://docs.redpesk.bzh/docs/en/master/getting_started/docs/deployment.html)
- [Booting a redpesk image with QEMU](https://docs.redpesk.bzh/docs/en/master/download/boards/docs/boards/qemu.html)

## Troubleshooting

If the binder cannot load the local binding, first verify that both the Cargo output and deployment-name symlink exist:

```bash
ls -l ./target/release/libhelloworld_rust_binding.so \
      ./target/release/helloworld-rust-binding.so
```

For an installed package, verify its contents with:

```bash
rpm -ql helloworld-rust-binding
```

Increase binder verbosity when diagnosing local API loading or request handling issues:

```bash
afb-binder -vvvv -b ./target/release/helloworld-rust-binding.so
```

For Cargo dependency or compilation failures, rerun the build with verbose Cargo output:

```bash
cargo build --release --package helloworld-rust-binding -vv
```
