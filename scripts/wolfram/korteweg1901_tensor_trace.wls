(* Blackboard-level finite Cartesian trace for Korteweg 1901 Eq. (20).
   This verifies explicit transitions; it does not prove a continuum PDE or
   establish an Onuki equivalence. *)

ClearAll["Global`*"];

failures = {};
traceRows = {};

recordStep[id_String, anchor_String, input_, transformation_String,
    assumptions_String, output_, residual_, expected_String] := Module[
  {reduced, status},
  reduced = FullSimplify[Expand[residual]];
  status = Which[
    expected === "ZERO" && TrueQ[reduced === 0], "PASS_ZERO",
    expected === "NONZERO" && ! TrueQ[reduced === 0], "PASS_EXPECTED_NONZERO",
    True, "FAIL"
  ];
  AppendTo[traceRows, {
    id, anchor, ToString[input, InputForm], transformation, assumptions,
    ToString[output, InputForm], ToString[reduced, InputForm], status
  }];
  Print[id <> "\t" <> status <> "\t" <> ToString[reduced, InputForm]];
  If[status === "FAIL", AppendTo[failures, {id, reduced, expected}]];
];

x = Unique["x"];
y = Unique["y"];
r = rho[x, y];
rx = D[r, x]; ry = D[r, y];
rxx = D[r, {x, 2}]; rxy = D[r, x, y]; ryy = D[r, {y, 2}];
q = rx^2 + ry^2;
lap = rxx + ryy;
grad = {rx, ry};
hess = {{rxx, rxy}, {rxy, ryy}};
identity = IdentityMatrix[2];

compact = (alpha[x, y] q - gamma[x, y] lap) identity +
  beta[x, y] Outer[Times, grad, grad] - deltaK[x, y] hess;
sourceComponents = {
  {alpha[x, y] q + beta[x, y] rx^2 - gamma[x, y] lap - deltaK[x, y] rxx,
   beta[x, y] rx ry - deltaK[x, y] rxy},
  {beta[x, y] ry rx - deltaK[x, y] rxy,
   alpha[x, y] q + beta[x, y] ry^2 - gamma[x, y] lap - deltaK[x, y] ryy}
};

recordStep["KT01", "Korteweg Eq. (20), p. 12", compact,
  "Expand compact isotropic/dyadic/Hessian tensor into components",
  "Cartesian coordinates; rho in C2", sourceComponents,
  Total[Flatten[compact - sourceComponents]^2], "ZERO"];

directX = D[sourceComponents[[1, 1]], x] + D[sourceComponents[[1, 2]], y];
directY = D[sourceComponents[[2, 1]], x] + D[sourceComponents[[2, 2]], y];
recordStep["KT02", "KT01", sourceComponents,
  "Define each row divergence by summing derivatives over the second index",
  "Coefficient fields in C1; rho in C3", {directX, directY},
  Total[({directX, directY} - {
    D[sourceComponents[[1, 1]], x] + D[sourceComponents[[1, 2]], y],
    D[sourceComponents[[2, 1]], x] + D[sourceComponents[[2, 2]], y]
  })^2], "ZERO"];

alphaInputX = D[alpha[x, y] q, x];
alphaOutputX = q D[alpha[x, y], x] + 2 alpha[x, y] (rxx rx + rxy ry);
recordStep["KT03", "KT02", alphaInputX, "Product rule",
  "rho in C2", alphaOutputX, alphaInputX - alphaOutputX, "ZERO"];

gammaInputX = D[gamma[x, y] lap, x];
gammaOutputX = lap D[gamma[x, y], x] + gamma[x, y] D[lap, x];
recordStep["KT04", "KT02", gammaInputX, "Product rule",
  "rho in C3", gammaOutputX, gammaInputX - gammaOutputX, "ZERO"];

betaInputX = D[beta[x, y] rx^2, x] + D[beta[x, y] rx ry, y];
betaOutputX = rx (D[beta[x, y], x] rx + D[beta[x, y], y] ry) +
  beta[x, y] (rxx rx + rxy ry) + beta[x, y] rx lap;
recordStep["KT05", "KT02", betaInputX, "Two-dimensional dyadic product rule",
  "rho in C2", betaOutputX, betaInputX - betaOutputX, "ZERO"];

deltaInputX = D[deltaK[x, y] rxx, x] + D[deltaK[x, y] rxy, y];
deltaOutputX = D[deltaK[x, y], x] rxx + D[deltaK[x, y], y] rxy +
  deltaK[x, y] D[lap, x];
recordStep["KT06", "KT02", deltaInputX, "Hessian product rule and commuting derivatives",
  "rho in C3", deltaOutputX, deltaInputX - deltaOutputX, "ZERO"];

collectedX = q D[alpha[x, y], x] - lap D[gamma[x, y], x] +
  rx (D[beta[x, y], x] rx + D[beta[x, y], y] ry) -
  (D[deltaK[x, y], x] rxx + D[deltaK[x, y], y] rxy) +
  (2 alpha[x, y] + beta[x, y]) (rxx rx + rxy ry) +
  beta[x, y] rx lap - (gamma[x, y] + deltaK[x, y]) D[lap, x];
recordStep["KT07", "KT03--KT06", directX, "Expand and Collect",
  "rho in C3; coefficient fields in C1", collectedX,
  directX - collectedX, "ZERO"];

collectedY = q D[alpha[x, y], y] - lap D[gamma[x, y], y] +
  ry (D[beta[x, y], x] rx + D[beta[x, y], y] ry) -
  (D[deltaK[x, y], x] rxy + D[deltaK[x, y], y] ryy) +
  (2 alpha[x, y] + beta[x, y]) (rxy rx + ryy ry) +
  beta[x, y] ry lap - (gamma[x, y] + deltaK[x, y]) D[lap, y];
recordStep["KT08", "KT03--KT06", directY, "Expand and Collect",
  "rho in C3; coefficient fields in C1", collectedY,
  directY - collectedY, "ZERO"];

stateChainInput = D[a[rho[x, y], theta[x, y]], x];
stateChainOutput = Derivative[1, 0][a][rho[x, y], theta[x, y]] D[rho[x, y], x] +
  Derivative[0, 1][a][rho[x, y], theta[x, y]] D[theta[x, y], x];
recordStep["KT09", "Coefficient state dependence", stateChainInput,
  "Two-variable chain rule", "a in C1; rho and theta in C1",
  stateChainOutput, stateChainInput - stateChainOutput, "ZERO"];

recordStep["KT10", "Korteweg Eq. (1), p. 1", body - divP,
  "Substitute divSigma=-divP", "same divergence convention",
  body + divSigma, (body - divP) - (body + divSigma /. divSigma -> -divP), "ZERO"];

chi = x^2 y^2;
recordStep["KT11", "Modern scalar-gauge guardrail", chi IdentityMatrix[2],
  "Take row divergence", "chi in C1", {D[chi, x], D[chi, y]},
  D[chi, x], "NONZERO"];

polyRules = {
  rho -> Function[{xx, yy}, 1 + xx^2 + xx yy + yy^3],
  alpha -> Function[{xx, yy}, 1 + xx],
  beta -> Function[{xx, yy}, 2 + yy],
  gamma -> Function[{xx, yy}, 3 + xx yy],
  deltaK -> Function[{xx, yy}, 4 + xx^2]
};
wrongSignResidual = FullSimplify[(2 directX) /. polyRules];
recordStep["KT12", "KT10", divP, "Use wrong sign sigma=+P in polynomial witness",
  "nontrivial rho and coefficient fields", -divP,
  wrongSignResidual, "NONZERO"];

coefficientDerivativePartX = q D[alpha[x, y], x] - lap D[gamma[x, y], x] +
  rx (D[beta[x, y], x] rx + D[beta[x, y], y] ry) -
  (D[deltaK[x, y], x] rxx + D[deltaK[x, y], y] rxy);
omittedCoefficientResidual = FullSimplify[coefficientDerivativePartX /. polyRules];
recordStep["KT13", "KT07", collectedX,
  "Delete coefficient-derivative terms in a nonconstant polynomial witness",
  "nonconstant coefficient fields", collectedX - coefficientDerivativePartX,
  omittedCoefficientResidual, "NONZERO"];

airy = {{D[chi, {y, 2}], -D[chi, x, y]},
        {-D[chi, x, y], D[chi, {x, 2}]}};
airyDiv = {D[airy[[1, 1]], x] + D[airy[[1, 2]], y],
           D[airy[[2, 1]], x] + D[airy[[2, 2]], y]};
recordStep["KT14", "Modern divergence-free gauge guardrail", airy,
  "Take row divergence of an Airy tensor", "chi in C3", {0, 0},
  Total[airyDiv^2], "ZERO"];

projectRoot = Nest[DirectoryName, $InputFileName, 3];
generatedDir = FileNameJoin[{projectRoot, "generated", "wolfram"}];
If[! DirectoryQ[generatedDir], CreateDirectory[generatedDir, CreateIntermediateDirectories -> True]];
headers = {"trace_id", "anchor", "input", "transformation", "assumptions", "output", "residual", "status"};
Export[FileNameJoin[{generatedDir, "korteweg1901_tensor_trace.tsv"}], Prepend[traceRows, headers], "TSV"];
markdown = "# Korteweg 1901 tensor trace\n\n" <>
  StringRiffle[("- `" <> #[[1]] <> "` " <> #[[8]] <> ": residual `" <> #[[7]] <> "`") & /@ traceRows, "\n"] <> "\n";
Export[FileNameJoin[{generatedDir, "korteweg1901_tensor_trace.md"}], markdown, "Text"];

If[Length[failures] > 0,
  Print["FAIL: Korteweg 1901 tensor Wolfram trace"];
  Print[failures // InputForm];
  Exit[1],
  Print["PASS: Korteweg 1901 tensor Wolfram trace"];
  Exit[0]
];
