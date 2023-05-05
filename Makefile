all: build

build:
	dune build --profile dev
	@[ -L while ] || ln -s _build/default/bin/while.exe while
	@[ -L w3a ] || ln -s _build/default/bin/w3a.exe w3a
	@[ -L compile ] || ln -s _build/default/bin/compile.exe compile
	@[ -L repair ] || ln -s _build/default/bin/repair.exe repair
test:
	@dune runtest

clean:
	@dune clean
	@rm -rf compile analyze while w3a

.PHONY: all build clean test
