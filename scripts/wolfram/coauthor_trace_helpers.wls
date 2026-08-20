(* Shared structured trace emitter for atomic finite checks.
   Multi-step suites retain their dedicated transition-table implementations. *)

ClearAll[recordAtomicTrace];

recordAtomicTrace[id_String, anchor_String, premise_String, input_,
    transformation_String, assumptions_String, output_, residual_,
    expected_String] := Print[StringRiffle[{
  "TRACE", id, anchor, premise, ToString[input, InputForm], transformation,
  assumptions, ToString[output, InputForm], ToString[residual, InputForm],
  expected
}, "\t"]];
