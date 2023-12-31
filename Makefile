VERSION=$(shell cat VERSION)

ifeq ($(shell uname -s),Darwin)
CONFIG_DARWIN=y
else ifeq ($(OS),Windows_NT)
CONFIG_WINDOWS=y
else
CONFIG_LINUX=y
endif

LIBRARY_PREFIX=lib
ifdef CONFIG_DARWIN
LOADABLE_EXTENSION=dylib
endif

ifdef CONFIG_LINUX
LOADABLE_EXTENSION=so
endif


ifdef CONFIG_WINDOWS
LOADABLE_EXTENSION=dll
LIBRARY_PREFIX=
endif

prefix=dist
TARGET_LOADABLE=$(prefix)/debug/robotstxt0.$(LOADABLE_EXTENSION)
TARGET_LOADABLE_RELEASE=$(prefix)/release/robotstxt0.$(LOADABLE_EXTENSION)

TARGET_STATIC=$(prefix)/debug/robotstxt0.a
TARGET_STATIC_RELEASE=$(prefix)/release/robotstxt0.a

TARGET_WHEELS=$(prefix)/debug/wheels
TARGET_WHEELS_RELEASE=$(prefix)/release/wheels

INTERMEDIATE_PYPACKAGE_EXTENSION=bindings/python/sqlite_robotstxt/robotstxt0.$(LOADABLE_EXTENSION)

ifdef target
CARGO_TARGET=--target=$(target)
BUILT_LOCATION=target/$(target)/debug/$(LIBRARY_PREFIX)sqlite_robotstxt.$(LOADABLE_EXTENSION)
BUILT_LOCATION_RELEASE=target/$(target)/release/$(LIBRARY_PREFIX)sqlite_robotstxt.$(LOADABLE_EXTENSION)
else
CARGO_TARGET=
BUILT_LOCATION=target/debug/$(LIBRARY_PREFIX)sqlite_robotstxt.$(LOADABLE_EXTENSION)
BUILT_LOCATION_RELEASE=target/release/$(LIBRARY_PREFIX)sqlite_robotstxt.$(LOADABLE_EXTENSION)
endif

ifdef python
PYTHON=$(python)
else
PYTHON=python3
endif

ifdef IS_MACOS_ARM
RENAME_WHEELS_ARGS=--is-macos-arm
else
RENAME_WHEELS_ARGS=
endif

$(prefix):
	mkdir -p $(prefix)/debug
	mkdir -p $(prefix)/release

$(TARGET_WHEELS): $(prefix)
	mkdir -p $(TARGET_WHEELS)

$(TARGET_WHEELS_RELEASE): $(prefix)
	mkdir -p $(TARGET_WHEELS_RELEASE)

$(TARGET_LOADABLE): $(prefix) $(shell find . -type f -name '*.rs')
	cargo build $(CARGO_TARGET)
	cp $(BUILT_LOCATION) $@

$(TARGET_LOADABLE_RELEASE): $(prefix) $(shell find . -type f -name '*.rs')
	cargo build --release $(CARGO_TARGET)
	cp $(BUILT_LOCATION_RELEASE) $@

python: $(TARGET_WHEELS) $(TARGET_LOADABLE) bindings/python/setup.py bindings/python/sqlite_robotstxt/__init__.py .github/workflows/rename-wheels.py
	cp $(TARGET_LOADABLE) $(INTERMEDIATE_PYPACKAGE_EXTENSION)
	rm $(TARGET_WHEELS)/sqlite_robotstxt* || true
	pip3 wheel bindings/python/ -w $(TARGET_WHEELS)
	python3 .github/workflows/rename-wheels.py $(TARGET_WHEELS) $(RENAME_WHEELS_ARGS)

python-release: $(TARGET_LOADABLE_RELEASE) $(TARGET_WHEELS_RELEASE) bindings/python/setup.py bindings/python/sqlite_robotstxt/__init__.py .github/workflows/rename-wheels.py
	cp $(TARGET_LOADABLE_RELEASE)  $(INTERMEDIATE_PYPACKAGE_EXTENSION)
	rm $(TARGET_WHEELS_RELEASE)/sqlite_robotstxt* || true
	pip3 wheel bindings/python/ -w $(TARGET_WHEELS_RELEASE)
	python3 .github/workflows/rename-wheels.py $(TARGET_WHEELS_RELEASE) $(RENAME_WHEELS_ARGS)

datasette: $(TARGET_WHEELS) bindings/datasette/setup.py bindings/datasette/datasette_sqlite_robotstxt/__init__.py
	rm $(TARGET_WHEELS)/datasette* || true
	pip3 wheel bindings/datasette/ --no-deps -w $(TARGET_WHEELS)

datasette-release: $(TARGET_WHEELS_RELEASE) bindings/datasette/setup.py bindings/datasette/datasette_sqlite_robotstxt/__init__.py
	rm $(TARGET_WHEELS_RELEASE)/datasette* || true
	pip3 wheel bindings/datasette/ --no-deps -w $(TARGET_WHEELS_RELEASE)

bindings/sqlite-utils/pyproject.toml: bindings/sqlite-utils/pyproject.toml.tmpl VERSION
	VERSION=$(VERSION) envsubst < $< > $@
	echo "✅ generated $@"

bindings/sqlite-utils/sqlite_utils_sqlite_robotstxt/version.py: bindings/sqlite-utils/sqlite_utils_sqlite_robotstxt/version.py.tmpl VERSION
	VERSION=$(VERSION) envsubst < $< > $@
	echo "✅ generated $@"

sqlite-utils: $(TARGET_WHEELS) bindings/sqlite-utils/pyproject.toml bindings/sqlite-utils/sqlite_utils_sqlite_robotstxt/version.py
	python3 -m build bindings/sqlite-utils -w -o $(TARGET_WHEELS)

sqlite-utils-release: $(TARGET_WHEELS) bindings/sqlite-utils/pyproject.toml bindings/sqlite-utils/sqlite_utils_sqlite_robotstxt/version.py
	python3 -m build bindings/sqlite-utils -w -o $(TARGET_WHEELS_RELEASE)

npm: VERSION bindings/node/platform-package.README.md.tmpl bindings/node/platform-package.package.json.tmpl bindings/node/sqlite-robotstxt/package.json.tmpl scripts/node_generate_platform_packages.sh
	scripts/node_generate_platform_packages.sh

deno: VERSION bindings/deno/deno.json.tmpl
	scripts/deno_generate_package.sh

Cargo.toml: VERSION
	cargo set-version `cat VERSION`

bindings/python/sqlite_robotstxt/version.py: VERSION
	printf '__version__ = "%s"\n__version_info__ = tuple(__version__.split("."))\n' `cat VERSION` > $@

bindings/python/datasette_sqlite_robotstxt/version.py: VERSION
	printf '__version__ = "%s"\n__version_info__ = tuple(__version__.split("."))\n' `cat VERSION` > $@

bindings/ruby/lib/version.rb: bindings/ruby/lib/version.rb.tmpl VERSION
	VERSION=$(VERSION) envsubst < $< > $@

ruby: bindings/ruby/lib/version.rb

version:
	make Cargo.toml
	make bindings/python/sqlite_robotstxt/version.py
	make bindings/datasette/datasette_sqlite_robotstxt/version.py
	make bindings/sqlite-utils/pyproject.toml bindings/sqlite-utils/sqlite_utils_sqlite_robotstxt/version.py
	make npm
	make deno
	make ruby

# ███████████████████████████████ WASM SECTION ███████████████████████████████

SQLITE_WASM_VERSION=3440000
SQLITE_WASM_YEAR=2023
SQLITE_WASM_SRCZIP=$(prefix)/sqlite-src.zip
SQLITE_WASM_COMPILED_SQLITE3C=$(prefix)/sqlite-src-$(SQLITE_WASM_VERSION)/sqlite3.c
SQLITE_WASM_COMPILED_MJS=$(prefix)/sqlite-src-$(SQLITE_WASM_VERSION)/ext/wasm/jswasm/sqlite3.mjs
SQLITE_WASM_COMPILED_WASM=$(prefix)/sqlite-src-$(SQLITE_WASM_VERSION)/ext/wasm/jswasm/sqlite3.wasm

TARGET_WASM_LIB=$(prefix)/libsqlite_robotstxt.wasm.a
TARGET_WASM_MJS=$(prefix)/sqlite3.mjs
TARGET_WASM_WASM=$(prefix)/sqlite3.wasm
TARGET_WASM=$(TARGET_WASM_MJS) $(TARGET_WASM_WASM)

$(SQLITE_WASM_SRCZIP):
	curl -o $@ https://www.sqlite.org/$(SQLITE_WASM_YEAR)/sqlite-src-$(SQLITE_WASM_VERSION).zip

$(SQLITE_WASM_COMPILED_SQLITE3C): $(SQLITE_WASM_SRCZIP)
	unzip -q -o $< -d $(prefix)
	(cd $(prefix)/sqlite-src-$(SQLITE_WASM_VERSION)/ && ./configure --enable-all && make sqlite3.c)

$(TARGET_WASM_LIB): $(shell find src -type f -name '*.rs')
	RUSTFLAGS="-Clink-args=-sERROR_ON_UNDEFINED_SYMBOLS=0 -Clink-args=--no-entry" \
		cargo build --release --target wasm32-unknown-emscripten --features=static
		cp target/wasm32-unknown-emscripten/release/libsqlite_robotstxt.a $@

$(SQLITE_WASM_COMPILED_MJS) $(SQLITE_WASM_COMPILED_WASM): $(SQLITE_WASM_COMPILED_SQLITE3C) $(TARGET_WASM_LIB)
	(cd $(prefix)/sqlite-src-$(SQLITE_WASM_VERSION)/ext/wasm && \
		make sqlite3_wasm_extra_init.c=../../../libsqlite_robotstxt.wasm.a "emcc.flags=-s EXTRA_EXPORTED_RUNTIME_METHODS=['ENV'] -s FETCH")

$(TARGET_WASM_MJS): $(SQLITE_WASM_COMPILED_MJS)
	cp $< $@

$(TARGET_WASM_WASM): $(SQLITE_WASM_COMPILED_WASM)
	cp $< $@

wasm: $(TARGET_WASM)

# ███████████████████████████████   END WASM   ███████████████████████████████


# ███████████████████████████████ SITE SECTION ███████████████████████████████

WASM_TOOLKIT_NPM_TGZ=$(prefix)/sqlite-wasm-toolkit-npm.tgz

TARGET_SITE_DIR=$(prefix)/site
TARGET_SITE=$(prefix)/site/index.html

$(WASM_TOOLKIT_NPM_TGZ):
	curl -o $@ -q https://registry.npmjs.org/@alex.garcia/sqlite-wasm-toolkit/-/sqlite-wasm-toolkit-0.0.1-alpha.7.tgz

$(TARGET_SITE_DIR)/slim.js $(TARGET_SITE_DIR)/slim.css: $(WASM_TOOLKIT_NPM_TGZ)
	tar -xvzf $< -C $(TARGET_SITE_DIR) --strip-components=2 package/dist/slim.js package/dist/slim.css


$(TARGET_SITE_DIR):
	mkdir -p $(TARGET_SITE_DIR)

$(TARGET_SITE): site/index.html $(TARGET_SITE_DIR) $(TARGET_WASM_MJS) $(TARGET_WASM_WASM) $(TARGET_SITE_DIR)/slim.js $(TARGET_SITE_DIR)/slim.css
	cp $(TARGET_WASM_MJS) $(TARGET_SITE_DIR)
	cp $(TARGET_WASM_WASM) $(TARGET_SITE_DIR)
	cp $< $@
site: $(TARGET_SITE)
# ███████████████████████████████   END SITE   ███████████████████████████████


format:
	cargo fmt

sqlite-robotstxt.h: cbindgen.toml
	rustup run nightly cbindgen  --config $< -o $@

release: $(TARGET_LOADABLE_RELEASE) $(TARGET_STATIC_RELEASE)

loadable: $(TARGET_LOADABLE)
loadable-release: $(TARGET_LOADABLE_RELEASE)

static: $(TARGET_STATIC)
static-release: $(TARGET_STATIC_RELEASE)

debug: loadable static python datasette
release: loadable-release static-release python-release datasette-release

clean:
	rm dist/*
	cargo clean

test-loadable:
	$(PYTHON) tests/test-loadable.py


test-npm:
	node bindings/node/sqlite-robotstxt/test.js

test-deno:
	deno task --config bindings/deno/deno.json test

test:
	make test-loadable
	make test-npm
	make test-deno

publish-release:
	./scripts/publish_release.sh

.PHONY: clean \
	test test-loadable test-npm test-deno \
	loadable loadable-release \
	python python-release \
	datasette datasette-release \
	sqlite-utils sqlite-utils-release \
	static static-release \
	debug release \
	format version publish-release \
	npm deno ruby \
	wasm
