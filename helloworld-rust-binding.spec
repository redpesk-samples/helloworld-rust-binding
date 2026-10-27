%global debug_package %{nil}

Name:    helloworld-rust-binding
Version: 2.0.0
Release: 2%{?dist}
License: MIT
Summary: Rust helloworld service used in redpesk
URL:     https://github.com/redpesk-samples/helloworld-rust-binding
Source:  %{name}-%{version}.tar.gz
Source1: vendor.tar.bz2
Source2: cargo_config

%global _afmappdir %{_prefix}/redpesk
%global redtest_dir %{_libexecdir}/redtest/%{name}
%global coverage_dir %{redtest_dir}/coverage_data
%global coverage_srcdir %{redtest_dir}/sources

BuildRequires: cargo
BuildRequires: rust
BuildRequires: gcc
BuildRequires: clang-devel
BuildRequires: pkgconfig(json-c)
BuildRequires: pkgconfig(afb-binding)

%description
Provides the Rust implementation of the redpesk helloworld API. It exposes
exactly the same application API as helloworld-binding: info, hello, sum and
the verb_called event.

%package redtest
Summary: redtest package with LLVM coverage build
Requires: %{name} = %{version}-%{release}
Requires: afb-test-py
Requires: afb-libpython
Requires: llvm

%description redtest
This package contains the functional redtest assets, an LLVM coverage-
instrumented Rust binding and the corresponding source files.

%prep
%autosetup -p 1

tar -xjf %{SOURCE1}
mkdir -p .cargo
cp %{SOURCE2} .cargo/config

%build
# Build the production binding without coverage instrumentation.
export CARGO_TARGET_DIR="%{_builddir}/%{name}-%{version}/target-release"
unset RUSTFLAGS
cargo build \
    --offline \
    --locked \
    --release \
    --package helloworld-rust-binding \
    --target %{_arch}-unknown-linux-gnu

# Build a separate binding for redtest with LLVM coverage instrumentation.
export CARGO_TARGET_DIR="%{_builddir}/%{name}-%{version}/target-coverage"
export RUSTFLAGS="-C instrument-coverage -C debuginfo=2 -C link-dead-code --remap-path-prefix=%{_builddir}/%{name}-%{version}=%{coverage_srcdir}"
cargo build \
    --offline \
    --locked \
    --release \
    --package helloworld-rust-binding \
    --target %{_arch}-unknown-linux-gnu

# Keep the existing RPM-build test pass on the instrumented build.
cargo test \
    --offline \
    --locked \
    --release \
    --all-targets \
    --all-features \
    --target %{_arch}-unknown-linux-gnu

%install
# Production binding.
install -d %{buildroot}%{_afmappdir}/%{name}/lib
install -d %{buildroot}%{_afmappdir}/%{name}/.rpconfig
install -m 0755 \
    target-release/%{_arch}-unknown-linux-gnu/release/libhelloworld_rust_binding.so \
    %{buildroot}%{_afmappdir}/%{name}/lib/helloworld-rust-binding.so
install -m 0644 rpconfig/manifest.yml \
    %{buildroot}%{_afmappdir}/%{name}/.rpconfig/manifest.yml

# RedTest assets.
install -Dm0755 redtest/run-redtest \
    %{buildroot}%{redtest_dir}/run-redtest
install -Dm0644 tests/tests.py \
    %{buildroot}%{redtest_dir}/tests.py

# Coverage-instrumented binding used only by redtest.
install -d %{buildroot}%{coverage_dir}/%{name}/lib
install -m 0755 \
    target-coverage/%{_arch}-unknown-linux-gnu/release/libhelloworld_rust_binding.so \
    %{buildroot}%{coverage_dir}/%{name}/lib/helloworld-rust-binding.so

# Package the Rust sources referenced by the coverage metadata.
mkdir -p %{buildroot}%{coverage_srcdir}
cp -a src %{buildroot}%{coverage_srcdir}/

# Fail the RPM build if the dedicated coverage payload is incomplete.
test -f %{buildroot}%{coverage_dir}/%{name}/lib/helloworld-rust-binding.so
test -f %{buildroot}%{coverage_srcdir}/src/lib.rs

%files
%defattr(-,root,root)
%license LICENSE
%doc README.md CHANGELOG
%dir %{_afmappdir}/%{name}
%{_afmappdir}/%{name}/lib/
%{_afmappdir}/%{name}/.rpconfig/

%files redtest
%defattr(-,root,root)
%{redtest_dir}/run-redtest
%{redtest_dir}/tests.py
%{coverage_dir}
%{coverage_srcdir}

%changelog
