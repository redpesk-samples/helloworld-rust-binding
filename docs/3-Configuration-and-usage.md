# Configuration and usage

## Runtime configuration

`helloworld-rust-binding` does not require an application-specific runtime configuration file. It is a loadable AFB V4 binding and is configured through the `afb-binder` command line.

For the complete binder command-line interface, refer to the [`afb-binder` manual](https://docs.redpesk.bzh/docs/en/master/redpesk-os/afb-binder/afb-binder.1.html).

When installed as a redpesk package, `.rpconfig/manifest.yml` declares the packaged service and the provided `helloworld` API.

## Run a source build

After `make build`, start `afb-binder` and load the binding from the Cargo release directory:

```bash
afb-binder -vvv -b ./target/release/helloworld-rust-binding.so
```

Unless another port is configured, the binder listens on port `1234`.

## Run the installed binding

For an RPM installation, load the packaged shared library:

```bash
afb-binder -vvv -b /usr/redpesk/helloworld-rust-binding/lib/helloworld-rust-binding.so
```

## Call the API

Use `afb-client` from another terminal.

Call `hello` without an argument:

```bash
afb-client -H localhost:1234/api helloworld hello
```

The reply contains:

```text
Hello world!
```

Call `hello` with a value:

```bash
afb-client -H localhost:1234/api helloworld hello Rust
```

The reply contains:

```text
Hello Rust!
```

Call `sum` with a JSON array of integers:

```bash
afb-client -H localhost:1234/api helloworld sum '[1,2,3,4]'
```

The returned value is `10`.

Retrieve the static binding metadata with:

```bash
afb-client -H localhost:1234/api helloworld info
```

The complete request and response contract is described in the [Api reference](./4-Api-reference.html).

## Events

Calls to `hello` and `sum` publish the `helloworld/verb_called` event. The caller is automatically subscribed the first time one of these verbs is called in its session.

For example, calling `hello` produces an event whose payload is the called verb name:

```json
{
  "event": "helloworld/verb_called",
  "data": "hello"
}
```

Subsequent calls reuse the session state and do not repeat the subscription setup.

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

Increase binder verbosity when diagnosing API loading or request handling issues:

```bash
afb-binder -vvvv -b ./target/release/helloworld-rust-binding.so
```

For Cargo dependency or compilation failures, rerun the build with verbose Cargo output:

```bash
cargo build --release --package helloworld-rust-binding -vv
```
