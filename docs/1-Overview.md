# Overview

## Purpose

`helloworld-rust-binding` is a minimal [AFB Binding V4](https://docs.redpesk.bzh/docs/en/master/developer-guides/afb-binding-tutorial-v4.html) example implemented in Rust with the [`afbv4`](https://github.com/redpesk-common/afb-librust) crate.

The project mirrors the public API of `helloworld-binding` and `helloworld-python-binding` while showing how the same service can be implemented as a Rust shared library loaded by `afb-binder`.

The sample demonstrates:

- creation of an AFB V4 API and verbs with `afbv4`;
- request conversion and typed replies;
- Rust `cdylib` integration with `afb-binder`;
- event creation, subscription and publication;
- per-client/session state management;
- signed 64-bit integer handling;
- functional validation with `afb-test-py` and redtest integration.

## Architecture

Cargo builds the project as a `cdylib`. The resulting shared library is loaded by `afb-binder` and registers the `helloworld` API during binding initialization.

```text
                 +----------------------+
                 |      AFB client      |
                 | afb-client / tests   |
                 +----------+-----------+
                            |
                            | AFB requests / events
                            v
                 +----------------------+
                 |      afb-binder      |
                 +----------+-----------+
                            |
                            v
                 +---------------------------+
                 | helloworld-rust-binding.so|
                 |                           |
                 | API: helloworld           |
                 | - hello                   |
                 | - sum                     |
                 | - info                    |
                 |                           |
                 | Event: verb_called        |
                 +---------------------------+
```

The binding itself does not depend on external hardware. It can therefore be executed on a development host, in a redpesk development environment (like using the [localbuilder](https://docs.redpesk.bzh/docs/en/master/getting_started/local_builder_quickstart/docs/quickstart/0_quick-installation.html)), or on a redpesk target (QEMU, aarch64 or x86_64 [target](https://docs.redpesk.bzh/docs/en/master/download/boards/docs/boards/download-images.html)).

## Binding lifecycle

`AfbBindingRegister!(binding_init)` registers the Rust initialization callback with AFB.

During initialization, `binding_init`:

1. creates the `verb_called` event;
2. creates the `info`, `hello` and `sum` verbs;
3. creates and finalizes the `helloworld` API;
4. returns the initialized API to the binder.

Initialization errors are propagated through the `Result` returned by `binding_init`.

## Client context and events

The binding uses an `AfbSessionRegister!` session context to track whether each client/session has already been subscribed to `verb_called`.

When a client calls `hello` or `sum`, the binding:

1. obtains or creates the session context;
2. subscribes the client when necessary;
3. publishes `helloworld/verb_called` with the called verb name as payload;
4. processes the request and sends the reply.

The event push is attempted before request validation, so rejected `sum` requests can still generate a `verb_called` event.

## Shared API contract

The Rust implementation exposes:

- API `helloworld`;
- verb `hello`;
- verb `sum`;
- verb `info`;
- event `helloworld/verb_called`.

The C/C++, Python and Rust samples expose the same public verbs and event and keep the same essential request semantics. Language-specific implementation details are intentionally not reproduced when they are not part of the shared AFB API contract.

The `info` metadata is embedded directly in `src/lib.rs` as a static JSON document and returned by the explicit `info` callback.

## Rust dependency model

The project depends on `afbv4` directly from the `afb-librust` Git repository as declared in `Cargo.toml`. The crate is not vendored in this repository.

Cargo therefore resolves the Rust dependency when building the project, subject to the configured Cargo cache and network environment.

## Project layout

The main project files are organized as follows:

```text
src/lib.rs                       Rust binding implementation
Cargo.toml                       Cargo package and dependency metadata
Makefile                         build, test and formatting helpers
rpconfig/manifest.yml            redpesk application manifest
redtest/run-redtest              redtest entry point
tests/                           functional tests and CI helper
docs/                            project documentation
helloworld-rust-binding.spec     RPM packaging
```
