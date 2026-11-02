%global debug_package %{nil}

%bcond_with coverage

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
%if %{with coverage}
Requires: llvm
%endif

%description redtest
This package contains the functional RedTest assets. When coverage is
enabled, it also provides the source files required by LLVM coverage.

%prep
%autosetup -p 1

tar -xjf %{SOURCE1}
mkdir -p .cargo
cp %{SOURCE2} .cargo/config

%build
# Build the production binding.
export CARGO_TARGET_DIR="%{_builddir}/%{name}-%{version}/target-release"

%if %{with coverage}
export RUSTFLAGS="-C instrument-coverage -C debuginfo=2 -C link-dead-code --remap-path-prefix=%{_builddir}/%{name}-%{version}=%{coverage_srcdir}"
%else
unset RUSTFLAGS
%endif

cargo build \
    --offline \
    --locked \
    --release \
    --package helloworld-rust-binding \
    --target %{_arch}-unknown-linux-gnu

# Keep the RPM-build test pass available in all builds.
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
install -Dm0755 redtest/llvm-total.sh \
    %{buildroot}%{redtest_dir}/llvm-total.sh
install -Dm0644 tests/tests.py \
    %{buildroot}%{redtest_dir}/tests.py

%if %{with coverage}
# Package the source path referenced by the instrumented binding.
mkdir -p %{buildroot}%{coverage_srcdir}/src
install -m0644 src/lib.rs %{buildroot}%{coverage_srcdir}/src/lib.rs

# Enable LLVM coverage processing in the installed RedTest runner.
sed -i 's/^COVERAGE=no$/COVERAGE=yes/' \
    %{buildroot}%{redtest_dir}/run-redtest
%endif

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
%{redtest_dir}/llvm-total.sh
%{redtest_dir}/tests.py
%if %{with coverage}
%{coverage_srcdir}
%endif

%changelog
