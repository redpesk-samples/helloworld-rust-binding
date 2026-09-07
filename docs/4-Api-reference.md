# Api reference

## API

The binding exposes the following AFB API:

```text
helloworld
```

It provides three verbs: `hello`, `sum` and `info`.

For the AFB V4 API model, verb declaration and request handling concepts used by this sample, see the [AFB Binding V4 tutorial](https://docs.redpesk.bzh/docs/en/master/developer-guides/afb-binding-tutorial-v4.html).

## `hello`

Returns a greeting.

### Request hello

The first argument is optional. When AFB can convert it to a string, that textual value is used in the reply. Additional arguments are ignored.

Without an argument:

```bash
afb-client -H localhost:1234/api helloworld hello
```

With an argument:

```bash
afb-client -H localhost:1234/api helloworld hello Rust
```

A missing argument or a JSON `null` value uses `world`.

### Reply hello

Without an argument:

```text
Hello world!
```

With `Rust` as the first argument:

```text
Hello Rust!
```

The Rust implementation returns the complete greeting as a Rust `String`; it does not impose an implementation-specific fixed-size reply buffer.

### Event hello

Each call publishes `helloworld/verb_called` with `hello` as payload after ensuring that the caller is subscribed.

## `sum`

Computes the sum of one JSON array of integers.

### Request sum

Exactly one argument is expected and it must be a JSON array containing only integers representable by the AFB/json-c integer type.

Example:

```bash
afb-client -H localhost:1234/api helloworld sum '[1,2,3,4]'
```

### Reply sum

The reply is a signed 64-bit integer containing the accumulated value.

For the previous example, the result is:

```text
10
```

An empty array returns `0`.

The Rust implementation uses `i64::wrapping_add` semantics while accumulating the array, so arithmetic overflow wraps in the signed 64-bit domain.

### Error sum

If the request does not contain exactly one parameter, if the parameter is not a JSON array, or if one of its elements is not an integer, the request fails with:

```text
parameter should be a JSON array of integers
```

### Event sum

The call publishes `helloworld/verb_called` with `sum` as payload before validating the request arguments. Invalid requests can therefore still produce the event.

## `info`

Returns the static metadata describing the sample API and its verbs.

### Request info

No argument is required:

```bash
afb-client -H localhost:1234/api helloworld info
```

### Reply info

The reply is a JSON object generated from the static metadata embedded in `src/lib.rs`. It describes the `helloworld` API and its `hello`, `sum` and `info` verbs.

The Rust binding disables the implicit AFB `info` and `ping` callbacks and registers this explicit `info` verb instead, keeping the sample API explicit and consistent across implementations.

## Event reference

### `helloworld/verb_called`

| Property | Value |
| --- | --- |
| Event name | `helloworld/verb_called` |
| Payload type | string |
| Payload | name of the called verb |
| Emitted by | `hello`, `sum` |
| Subscription | automatic, per client/session |

The session context records whether the current client has already been subscribed, preventing repeated subscription setup on subsequent requests.
