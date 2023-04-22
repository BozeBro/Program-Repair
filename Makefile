all: build

build:
	dune build --profile dev
	@[ -L w3a ] || ln -s _build/default/bin/w3a.exe w3a
test:
	@dune runtest

clean:
	@dune clean
	@rm -rf compile analyze while w3a

.PHONY: all build clean test
