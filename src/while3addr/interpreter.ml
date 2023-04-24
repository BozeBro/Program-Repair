open Core
open Lang

let initial_env = String.Map.empty
let get_int a = match a with Int x -> x | _ -> failwith "Not an Intger"
let get_arr a = match a with Int b -> failwith "Not an array" | Arr c -> c
let handle_op op a b = Int (op (get_int a) (get_int b))
let get_val arr v = Array.get (get_arr arr) (get_int v)
let handle_bool op a b = op (get_int a) (get_int b : int)

let update_arr env arrName ind newval lookup =
  let arr = get_arr (lookup env arrName) in
  Array.set arr ind newval

let eval_insn env pc insn =
  let update env id value = String.Map.set env ~key:id ~data:value in
  let lookup = String.Map.find_exn in
  match insn with
  | ConstAssign (v, n) ->
      let new_env = update env v (Int n) in
      `Continue (pc + 1, new_env)
  | VarAssign (v1, v2) ->
      let n = lookup env v2 in
      let new_env = update env v1 n in
      `Continue (pc + 1, new_env)
  | OpAssign (v, v1, v2, op) ->
      let n1 = lookup env v1 in
      let n2 = lookup env v2 in
      let int_op =
        match op with
        | Add -> handle_op ( + )
        | Sub -> handle_op ( - )
        | Mul -> handle_op ( * )
        | Div -> handle_op ( / )
        | Get -> fun arr v -> Int (Array.get (get_arr arr) (get_int v))
      in
      let result = int_op n1 n2 in
      let new_env = update env v result in
      `Continue (pc + 1, new_env)
  | Goto location -> `Continue (location, env)
  | IfGoto (v, opr, lineno) ->
      let n = lookup env v in
      let comparison = match opr with LT -> ( < ) | EQ -> ( = ) in
      if comparison (get_int n) 0 then `Continue (lineno, env)
      else `Continue (pc + 1, env)
  | Print v ->
      let printer x =
        print_int x;
        print_string " "
      in
      let n = lookup env v in
      let () =
        match n with
        | Int a -> Format.printf "%d\n" (get_int n)
        | Arr b ->
            Array.iter b ~f:printer;
            print_string "\n"
      in
      `Continue (pc + 1, env)
  | Halt -> `Halt
  | ConstAssignArray (name, len) ->
      let arr = Array.create ~len 0 in
      let env' = String.Map.remove env name in
      let new_env = update env' name (Arr arr) in
      `Continue (pc + 1, new_env)
  | VarAssignArray (name, n) ->
      let len = get_int (lookup env name) in
      let arr = Array.create ~len 0 in
      let env' = String.Map.remove env name in
      let new_env = update env' name (Arr arr) in
      `Continue (pc + 1, new_env)
  | UpdateCC (arrName, ind, newVal) ->
      update_arr env arrName ind newVal lookup;
      `Continue (pc + 1, env)
  | UpdateII (arrName, x, y) ->
      let ind = get_int (lookup env x) in
      let newVal = get_int (lookup env y) in
      update_arr env arrName ind newVal lookup;
      `Continue (pc + 1, env)
  | UpdateIC (arrName, x, newVal) ->
      let ind = get_int (lookup env x) in
      update_arr env arrName ind newVal lookup;
      `Continue (pc + 1, env)
  | UpdateCI (arrName, ind, y) ->
      let newVal = get_int (lookup env y) in
      update_arr env arrName ind newVal lookup;
      `Continue (pc + 1, env)

let rec eval_program env (pc, listing) =
  let fetch location =
    match Int.Map.find listing location with
    | None -> Format.sprintf "No instruction at %d" location |> failwith
    | Some instruction -> instruction
  in
  match eval_insn env pc (fetch pc) with
  | `Continue (next_pc, new_env) -> eval_program new_env (next_pc, listing)
  | `Halt -> ()
