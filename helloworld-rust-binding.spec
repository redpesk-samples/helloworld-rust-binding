Name:    helloworld-rust-binding
Version: 2.0.0
Release: 1%{?dist}
License: MIT
Summary: Rust helloworld service used in redpesk
URL:     https://github.com/redpesk-samples/helloworld-rust-binding
Source:  %{name}-%{version}.tar.gz
Source1: vendor.tar.bz2
Source2: cargo_config

%bcond_with no_coverage

%global _afmappdir %{_prefix}/redpesk
%global redtest_dir %{_libexecdir}/redtest/%{name}

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

%if %{without no_coverage}
%package redtest
Summary: redtest package (coverage build)
Requires: %{name} = %{version}-%{release}
Requires: afb-test-py
Requires: afb-libpython
Requires: llvm
%description redtest
This package contains the functional redtest assets and the Rust binding
built with LLVM coverage instrumentation.
%endif

%prep
%autosetup -p 1

tar -xjf %{SOURCE1}
mkdir -p .cargo
cp %{SOURCE2} .cargo/config

%build
export CARGO_TARGET_DIR="%{_builddir}/%{name}-%{version}/target"

%if %{without no_coverage}
export RUSTFLAGS="-C instrument-coverage -C debuginfo=2 -C link-dead-code"
%endif

cargo build \
            --offline \
            --locked \
            --release \
            --package helloworld-rust-binding \
            --target %{_arch}-unknown-linux-gnu

%if %{without no_coverage}
cargo test --release --all-targets --all-features
%endif

%install
install -d %{buildroot}%{_afmappdir}/%{name}/lib
install -d %{buildroot}%{_afmappdir}/%{name}/.rpconfig
install -m 0755 target/release/helloworld_rust_binding.so \
    %{buildroot}%{_afmappdir}/%{name}/lib/helloworld-rust-binding.so
install -m 0644 rpconfig/manifest.yml \
    %{buildroot}%{_afmappdir}/%{name}/.rpconfig/manifest.yml

%if %{without no_coverage}
# redtest package: keep a private copy of the instrumented binding next to
# the tests.
install -d %{buildroot}%{redtest_dir}/binding/lib
install -m 0755 target/release/helloworld_rust_binding.so \
    %{buildroot}%{redtest_dir}/binding/lib/helloworld-rust-binding.so
install -m 0755 redtest/run-redtest %{buildroot}%{redtest_dir}/run-redtest
install -m 0644 tests/tests.py %{buildroot}%{redtest_dir}/tests.py
%endif

%files
%defattr(-,root,root)
%dir %{_afmappdir}/%{name}
%{_afmappdir}/%{name}/lib/
%{_afmappdir}/%{name}/.rpconfig/

%if %{without no_coverage}
%files redtest
%defattr(-,root,root)
%{redtest_dir}/run-redtest
%{redtest_dir}/tests.py
%{redtest_dir}/binding/
%endif
