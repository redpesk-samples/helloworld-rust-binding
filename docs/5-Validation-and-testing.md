# Validation and testing

## Test strategy

The project provides functional compatibility tests and a [redtest integration](https://docs.redpesk.bzh/docs/en/master/getting_started/docs/quickstart/2_applications-sources.html) for execution in redpesk validation workflows.

The Python tests load the real Rust shared library through the AFB test framework. They exercise the shared API surface and core behavior while allowing Rust-specific implementation details to remain idiomatic.

The tests cover:

- `hello` replies with and without parameters;
- AFB string conversion for scalar, object and array values;
- signed 64-bit boundary and wrapping behavior;
- rejection of integers outside the supported AFB range at the client boundary;
- complete `hello` replies for long string arguments;
- `verb_called` event emission for `hello` and `sum`;
- valid `sum` requests, including empty arrays and signed 64-bit values;
- rejected `sum` requests;
- the explicit `info` verb.

## Test dependencies

The functional tests use `afb-test-py` and `afb-libpython`. The binding itself must already be buildable with the dependencies described in [Build and installation](./2-Build-and-installation.html).

Prepare one of the development environments described in [Build and installation](./2-Build-and-installation.html) before running the functional tests.

When using an RPM-based redpesk development environment, the Python test packages can alternatively be installed with:

```bash
sudo dnf install afb-libpython afb-test-py
```

## Run the functional tests

The simplest repository command builds the release library, creates the expected shared-library symlink and starts the tests:

```bash
make test
```

After an existing `make build`, the tests can also be run directly with:

```bash
./tests/run.sh
```

The helper exports `target/release` through `LD_LIBRARY_PATH`, refreshes the `helloworld-rust-binding.so` symlink and starts `tests/tests.py`.

To execute the Python test module manually after preparing the library path and symlink:

```bash
LD_LIBRARY_PATH=./target/release python3 ./tests/tests.py
```

To produce TAP output:

```bash
LD_LIBRARY_PATH=./target/release python3 ./tests/tests.py --tap
```

## Run lint checks

The CI lint helper verifies Rust formatting with `cargo fmt --check`:

```bash
./tests/ci/lint.sh
```

The same formatting can be applied locally with:

```bash
make fmt
```

The repository-level markdown configuration excludes the Apache `LICENSE` text from Markdown linting because the license is not a Markdown document.

## Redtest package

The RPM specification provides the `helloworld-rust-binding-redtest` subpackage. The default coverage-enabled RPM build instruments the binding installed by the main `helloworld-rust-binding` package. The redtest subpackage contains:

- `tests.py`;
- the `run-redtest` entry point.

The runner reuses `/usr/redpesk/helloworld-rust-binding/lib/helloworld-rust-binding.so` from the main package instead of packaging a duplicate copy.

Install it on a compatible redpesk test environment with:

```bash
dnf install helloworld-rust-binding helloworld-rust-binding-redtest
```

The installed test entry point is:

```text
/usr/libexec/redtest/helloworld-rust-binding/run-redtest
```

It can be executed directly with:

```bash
/usr/libexec/redtest/helloworld-rust-binding/run-redtest
```

## Test artifacts

The redtest runner writes its TAP result to:

```text
/var/log/redtest/helloworld-rust-binding/helloworld-rust.tap
```

The runner fails when the TAP report contains a `not ok` result, allowing it to be integrated into automated validation pipelines.

This RPM currently does not generate Rust code-coverage data as part of redtest.

## Continuous integration

The repository CI defines three stages:

1. `lint`, which runs `tests/ci/lint.sh`;
2. `build`, which uses the redpesk build template;
3. `redtest`, which runs after a successful build through the redpesk test template.
