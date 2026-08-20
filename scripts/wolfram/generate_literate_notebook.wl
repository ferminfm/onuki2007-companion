(* Generate an uncached Mathematica notebook expression for the public suite map.
   Use from a fresh desktop kernel: Get["scripts/wolfram/generate_literate_notebook.wl"]; *)

ClearAll[MakeLiterateNotebook];

MakeLiterateNotebook[output_: "Onuki2007Companion_Wolfram_Trace_Guide.nb"] := Module[
  {cells},
  cells = {
    Cell["Onuki 2007 Companion: Wolfram Trace Guide", "Title"],
    Cell["This notebook is generated from committed source. Evaluate cells top to bottom in a fresh kernel. It documents finite traces only and does not establish continuum or simulation claims.", "Text"],
    Cell["Run a suite from the repository root", "Section"],
    Cell[BoxData[ToBoxes[Get["scripts/wolfram/appendix_b_transition_trace.wls"]]], "Input"],
    Cell["Replace the example script with any entry in docs/wolfram-suite-manifest.json. Expected-nonzero rows are designed sensitivity controls, not source errata.", "Text"]
  };
  Put[Notebook[cells], output];
  Print["NOTEBOOK_SOURCE_WRITTEN: ", output];
];

Print["Load complete. Call MakeLiterateNotebook[] to write an uncached notebook expression."];
