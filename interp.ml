open Core
open Lang

let initial_env = String.Map.empty
let initial_arrs = String.Map.empty
let spawn n = Array.create ~len:n 0

let get env arrays arrName v1 n pc lookup update =
  let arr = lookup arrays arrName in
  let data = Array.get arr n in
  let new_env = update env v1 data in
  `Continue (pc + 1, new_env, arrays)

let update_arr arrays arrName ind newval lookup =
  let arr = lookup arrays arrName in
  Array.set arr ind newval

let eval_insn env arrays pc insn =
  let update env id value = String.Map.set env ~key:id ~data:value in
  let lookup = String.Map.find_exn in
  match insn with
  | ConstAssign (v, n) ->
      let new_env = update env v n in
      `Continue (pc + 1, new_env, arrays)
  | VarAssign (v1, v2) ->
      let n = lookup env v2 in
      let new_env = update env v1 n in
      `Continue (pc + 1, new_env, arrays)
  | OpAssign (v, v1, v2, op) ->
      let n1 = lookup env v1 in
      let n2 = lookup env v2 in
      let int_op =
        match op with
        | Add -> ( + )
        | Sub -> ( - )
        | Mul -> ( * )
        | Div -> ( / )
      in
      let result = int_op n1 n2 in
      let new_env = update env v result in
      `Continue (pc + 1, new_env, arrays)
  | Goto location -> `Continue (location, env, arrays)
  | IfGoto (v, opr, lineno) ->
      let n = lookup env v in
      let comparison = match opr with LT -> ( < ) | EQ -> ( = ) in
      if comparison n 0 then `Continue (lineno, env, arrays)
      else `Continue (pc + 1, env, arrays)
  | Print v ->
      let n = lookup env v in
      Format.printf "%d\n" n;
      `Continue (pc + 1, env, arrays)
  | Halt -> `Halt
  | VarAssignArray (v1, v) ->
      let n = lookup env v in
      let arr = spawn n in
      let new_arrays = update arrays v1 arr in
      `Continue (pc + 1, env, new_arrays)
  | ConstAssignArray (v1, n) ->
      let arr = spawn n in
      let new_arrays = update arrays v1 arr in
      `Continue (pc + 1, env, new_arrays)
  | ConstAssignGet (v1, arrName, n) ->
      get env arrays arrName v1 n pc lookup update
  | VarAssignGet (v1, arrName, y) ->
      let n = lookup env y in
      get env arrays arrName v1 n pc lookup update
  | UpdateCC (arrName, ind, newVal) ->
      update_arr arrays arrName ind newVal lookup;
      `Continue (pc + 1, env, arrays)
  | UpdateII (arrName, x, y) ->
      let ind = lookup env x in
      let newVal = lookup env y in
      update_arr arrays arrName ind newVal lookup;
      `Continue (pc + 1, env, arrays)
  | UpdateIC (arrName, x, newVal) ->
      let ind = lookup env x in
      update_arr arrays arrName ind newVal lookup;
      `Continue (pc + 1, env, arrays)
  | UpdateCI (arrName, ind, y) ->
      let newVal = lookup env y in
      update_arr arrays arrName ind newVal lookup;
      `Continue (pc + 1, env, arrays)

let rec eval_program env arrs (pc, listing) =
  let fetch location =
    match Int.Map.find listing location with
    | None -> Format.sprintf "No instruction at %d" location |> failwith
    | Some instruction -> instruction
  in
  match eval_insn env arrs pc (fetch pc) with
  | `Continue (next_pc, new_env, new_arrs) ->
      eval_program new_env new_arrs (next_pc, listing)
  | `Halt -> ()
