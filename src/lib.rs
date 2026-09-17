/*
 * SPDX-License-Identifier: Apache-2.0
 *
 * Rust implementation of redpesk-samples/helloworld-binding.
 */

use afbv4::prelude::*;

const INFO_VERB_JSON: &str = r#"{
    "metadata": {
        "uid": "helloworld",
        "info": "Hello world binding",
        "version": "2.0.0"
    },
    "groups": [
        {
            "uid": "helloworld",
            "info": "Hello world API",
            "verbs": [
                {
                    "uid": "hello",
                    "info": "Echoes the input argument",
                    "verb": "hello",
                    "sample": ["Bob", 42]
                },
                {
                    "uid": "sum",
                    "verb": "sum",
                    "info": "Sums the input arguments",
                    "sample": [[1, 2, 3, 10]]
                },
                {
                    "uid": "info",
                    "info": "Get binding info",
                    "verb": "info"
                }
            ]
        }
    ]
}"#;

const SUM_ERROR: &str = "parameter should be a JSON array of integers";

/// Shared verb context containing the event created for this API.
struct VerbContext {
    event: &'static AfbEvent,
}

AfbSessionRegister!(SessionContext);

/// Per-client/session state.
#[derive(Default)]
struct SessionContext {
    subscribed: bool,
}

/// Subscribe a client to `verb_called` the first time it calls hello/sum.
fn ensure_subscription(request: &AfbRequest, event: &'static AfbEvent) -> Result<(), AfbError> {
    let session = match SessionContext::get(request) {
        Ok(session) => session,
        Err(_) => {
            afb_log_msg!(Notice, request, "context initialized for new client");
            SessionContext::set(request, SessionContext::default())?
        },
    };

    if !session.subscribed {
        event.subscribe(request)?;
        session.subscribed = true;
    }

    Ok(())
}

/// Push the name of the called verb on the `verb_called` event.
fn publish_verb_called(request: &AfbRequest, ctx: &AfbCtxData) -> Result<(), AfbError> {
    let context = ctx.get_ref::<VerbContext>()?;
    ensure_subscription(request, context.event)?;
    let _ = context.event.push(request.get_verb().get_name());
    Ok(())
}

/// Reply with `Hello <value>!`, using AFB string conversion for the first argument.
fn hello_cb(request: &AfbRequest, args: &AfbRqtData, ctx: &AfbCtxData) -> Result<(), AfbError> {
    publish_verb_called(request, ctx)?;

    let who = args
        .get::<String>(0)
        .ok()
        .filter(|argument| argument != "null")
        .unwrap_or_else(|| "world".into());

    request.reply(format!("Hello {who}!"), 0);
    Ok(())
}

/// Parse and sum the single JSON integer array expected by the `sum` verb.
fn sum_values(args: &AfbRqtData) -> Result<i64, &'static str> {
    if args.get_count() != 1 {
        return Err(SUM_ERROR);
    }

    let array = args.get::<JsoncObj>(0).map_err(|_| SUM_ERROR)?;
    if !array.is_type(Jtype::Array) {
        return Err(SUM_ERROR);
    }

    (0..array.count().map_err(|_| SUM_ERROR)?).try_fold(0_i64, |sum, index| {
        let item = array.index::<JsoncObj>(index).map_err(|_| SUM_ERROR)?;
        if !item.is_type(Jtype::Int) {
            return Err(SUM_ERROR);
        }

        item.get_as::<i64>()
            .map(|value| sum.wrapping_add(value))
            .map_err(|_| SUM_ERROR)
    })
}

fn sum_error_reply(request: &AfbRequest, message: &'static str) {
    afb_log_msg!(Error, request, "{}", message);
    request.reply(message, -1);
}

/// Receives one JSON array of integers and replies with their i64 sum.
fn sum_cb(request: &AfbRequest, args: &AfbRqtData, ctx: &AfbCtxData) -> Result<(), AfbError> {
    publish_verb_called(request, ctx)?;

    let sum = match sum_values(args) {
        Ok(sum) => sum,
        Err(message) => {
            sum_error_reply(request, message);
            return Ok(());
        },
    };

    request.reply(sum, 0);
    Ok(())
}

/// Return the static metadata document describing this sample API.
fn info_cb(request: &AfbRequest, _args: &AfbRqtData, _ctx: &AfbCtxData) -> Result<(), AfbError> {
    match JsoncObj::parse(INFO_VERB_JSON) {
        Ok(info) => request.reply(info, 0),
        Err(_) => request.reply("error parsing info() verb description", -1),
    }
    Ok(())
}

/// Binding initialization callback.
pub fn binding_init(_rootv4: AfbApiV4, _jconf: JsoncObj) -> Result<&'static AfbApi, AfbError> {
    let verb_called = AfbEvent::new("verb_called").finalize()?;

    let info =
        AfbVerb::new("info").set_info("Get binding info").set_callback(info_cb).finalize()?;

    let hello = AfbVerb::new("hello")
        .set_info("Echoes the input argument")
        .set_usage("optional value convertible to string")
        .set_context(VerbContext { event: verb_called })
        .set_callback(hello_cb)
        .finalize()?;

    let sum = AfbVerb::new("sum")
        .set_info("Sums a JSON array of integers")
        .set_usage("one JSON array of signed integers")
        .set_context(VerbContext { event: verb_called })
        .set_callback(sum_cb)
        .finalize()?;

    let api = AfbApi::new("helloworld")
        .set_name("helloworld")
        .set_info("Hello world binding")
        .set_version("2.0.0")
        // Keep the sample API explicit instead of adding binder-generated verbs.
        .add_info_cb(false)
        .add_ping_cb(false)
        .add_event(verb_called)
        .add_verb(info)
        .add_verb(hello)
        .add_verb(sum)
        .finalize()?;

    Ok(api)
}

AfbBindingRegister!(binding_init);
