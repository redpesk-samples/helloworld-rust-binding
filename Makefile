.PHONY: all build test fmt clean link

all: build

build:
	cargo build --release --package helloworld-rust-binding
	$(MAKE) link

link:
	ln -sfn libhelloworld_rust_binding.so target/release/helloworld-rust-binding.so

test: build
	./tests/run.sh

fmt:
	cargo fmt --package helloworld-rust-binding

clean:
	cargo clean
