open Core
open While3addr
open Repair

let lexbuf = Lexing.from_channel In_channel.stdin
let prog = (1, Parser.listing Lexer.initial lexbuf)

(* let () = Interpreter.eval_program Interpreter.initial_env prog *)
let seen, exec =
  Coverage.getCoverage Interpreter.initial_env prog Coverage.coverageSeen
    Coverage.End

let () = Coverage.printLines (Coverage.invert End exec)
