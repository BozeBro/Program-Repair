open Core

type id = string
type lineno = int
type opr = LT | EQ
type op = Add | Sub | Mul | Div | Get
type var_t = Int of int | Arr of int array

type instr =
  | ConstAssign of id * int
  | VarAssign of id * id
  | OpAssign of id * id * id * op
  | Goto of lineno
  | IfGoto of id * opr * lineno
  | ConstAssignArray of id * int
  | VarAssignArray of id * id
  | UpdateII of id * id * id
  (* | UpdateIC of id * id * int
     | UpdateCI of id * int * id
     | UpdateCC of id * int * int *)
  | Print of id
  | Halt

type listing = instr Int.Map.t
type program = int * listing

let string_of_op = function
  | Add -> "+"
  | Sub -> "-"
  | Mul -> "*"
  | Div -> "/"
  | Get -> "!!"

let string_of_opr = function LT -> "<" | EQ -> "="

let string_of_instr i = function
  | ConstAssign (v, n) -> Format.sprintf "%d: %s := %d" i v n
  | VarAssign (v1, v2) -> Format.sprintf "%d: %s := %s" i v1 v2
  | OpAssign (v0, v1, v2, o) ->
      Format.sprintf "%d: %s := %s %s %s" i v0 v1 (string_of_op o) v2
  | Goto n -> Format.sprintf "%d: goto %d" i n
  | IfGoto (id, op, n) ->
      Format.sprintf "%d: if %s %s 0 goto %d" i id (string_of_opr op) n
  | Print id -> Format.sprintf "%d: print %s" i id
  | Halt -> Format.sprintf "%d: halt" i
  | VarAssignArray (v, len) -> Format.sprintf "%d: %s := array %s" i v len
  | ConstAssignArray (v, len) -> Format.sprintf "%d: %s := array %d" i v len
  (* | UpdateCC (v, a, b) -> Format.sprintf "%d: update %s %d %d" i v a b
     | UpdateCI (v, a, b) -> Format.sprintf "%d: update %s %d %s" i v a b
     | UpdateIC (v, a, b) -> Format.sprintf "%d: update %s %s %d" i v a b *)
  | UpdateII (v, a, b) -> Format.sprintf "%d: update %s %s %s" i v a b

let string_of_listing listing =
  Int.Map.fold_right listing ~init:[] ~f:(fun ~key:lineno ~data:i accum ->
      string_of_instr lineno i :: accum)
  |> String.concat ~sep:"\n"

let string_of_program (pc, listing) =
  Format.sprintf "PC: %d\nListing:\n%s" pc (string_of_listing listing)
