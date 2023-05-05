open Core
open While3addr.Lang
open While3addr
open Coverage

(*
    Find execution until we hit line number.
    Generate abstract value with given accessible functions
    Symbolically execute rest of the function, and gather all path contraints that lead to passing
*)

let rec execTillLine env (pc, listing) line =
  let instruction = fetch pc listing in
  match instruction with
  | Print _ -> execTillLine env (pc + 1, listing) line
  | _ -> (
      match Interpreter.eval_insn env pc instruction with
      | `Halt -> failwith "LineNumber not found"
      | `Continue (next_pc, new_env) ->
          if next_pc == line then ()
          else execTillLine new_env (next_pc, listing) line)




  
