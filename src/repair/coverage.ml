open Core
open While3addr

type opr = string
type arg = string
type stmt = string
type lineno = int

let coverageSeen = Int.Map.empty

type inst = Line of lineno * Lang.instr * inst | End

let rec printer = function
  | End -> ()
  | Line (line, instr, x) ->
      Printf.printf "%s\n" (Lang.string_of_instr line instr);
      printer x

let rec printLines = function
  | End -> ()
  | Line (line, _, End) -> Printf.printf "%d\n" line
  | Line (line, _, x) ->
      Printf.printf "%d " line;
      printLines x

let rec invert acc = function
  | End -> acc
  | Line (line, instr, x) ->
      let acc' = Line (line, instr, acc) in
      invert acc' x

let fetch location listing =
  match Int.Map.find listing location with
  | None -> Format.sprintf "No instruction at %d" location |> failwith
  | Some instruction -> instruction

(* type coverage =  *)
let rec getCoverage env (pc, listing) linesSeen execution =
  try
    let instruction = fetch pc listing in
    let linesSeen' =
      Int.Map.update linesSeen pc ~f:(function Some x -> x + 1 | None -> 1)
    in
    let execution' =
      match execution with
      | End -> Line (pc, instruction, End)
      | line -> Line (pc, instruction, line)
    in
    match instruction with
    | Print _ -> getCoverage env (pc + 1, listing) linesSeen' execution'
    | _ -> (
        match Interpreter.eval_insn env pc instruction with
        | `Halt -> (linesSeen', execution')
        | `Continue (next_pc, new_env) ->
            getCoverage new_env (next_pc, listing) linesSeen' execution')
  with _ -> (linesSeen, execution)
