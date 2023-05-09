# Instructions

- Install [opam](https://opam.ocaml.org/doc/Install.html) (these instructions
  assume opam version 2+).
  If you are using Windows, it is highly recommended that
  you use Windows Subsystem for Linux (WSL). More detailed instructions on how 
  to install opam on WSL can be found [here](https://github.com/janestreet/install-ocaml)
- Create a new switch using OCaml 4.14.0 (you can replace "homework" with any switch name you'd like; it's likely the code will work with other versions but we have only confirmed it works in 4.09.0 and 4.14.0)
```
opam init
opam switch create homework 4.14.0
eval $(opam env)
```
- Install dependencies:
```
opam install core dune merlin ounit2
```
- Build with `make`. This will create symlinks to four binaries. They are:
    - `while`: a While interpreter
    - `w3a`: a While3addr interpreter
    - `compile`: a While to While3addr compiler

  All of these binaries take input on stdin and output on stdout (i.e., you can
  run a While program by running `./while < program.while`, *not* by passing a
  file as input).
# Python 
Python requires a version of at least 3.10 to use (the project makes use of the new match statement).  It also needs z3 to solve constraints.
Install z3 via 
```
pip3 install z3-solver
```
The important python3 file entrypoints are `src/repair/repair.py` and `src/repair/interpreter.py`
repair.py takes two arguements, testPath and outPath,
testPath informs us of the Test Suite and outPath outputs a new program that passes all the test cases. 
Interpreter.py runs a w3a program along with  some given inputs.
`python3 src/repair/interpreter file args`. The file is a path to the file containing a valid a w3a program.
args is either an int for an integer argument, or a space separated list of integers to denote a list arguement. This implies that a w3a program only has a single input. 

File specification for writing a Test suite will loook like

buggyProgPath
input1 : output1
input2 : output2
inputn : outputn

Run `python src/repair/repair.py filePath outPath` 
will try to fix file at buggyProgPath and generate a program to try to pass the three tests given in the file. The generated program is located at outPath. 


# Resources

- You might be interested in reading Adam Chlipala's overview of the philosophic
  differences between OCaml and SML: http://adam.chlipala.net/mlcomp/
- This page has a nice side-by-side comparison of the syntax of SML and OCaml:
  https://people.mpi-sws.org/~rossberg/sml-vs-ocaml.html
- We are using the [Core library](https://ocaml.janestreet.com/ocaml-core/latest/doc/base/Base/index.html)
  maintained by Jane Street as it is more feature-rich than the OCaml standard
  library. The API documentation on that page should be useful.
- If you're using Vim or Emacs, [Merlin](https://ocaml.github.io/merlin/) is a
  very useful tool that adds features like autocompletion and function signature
  lookup. The [Merlin GitHub page](https://github.com/ocaml/merlin) will help
  you get set up.
- If you're using Emacs, [Tuareg mode](https://github.com/ocaml/tuareg) is a
  good editing mode.
- OCaml is a compiled or interpreted language, so it can be run in a
  [REPL](https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop). You
  can use the standard OCaml REPL, but we recommend
  [UTop](https://opam.ocaml.org/blog/about-utop/), which can be installed with
  `opam install utop`.
- The [official OCaml site](https://ocaml.org/learn/) has a lot of
  resources for learning OCaml.
- [Real World OCaml](https://realworldocaml.org/) is a great book for learning
  OCaml and is available free online.
