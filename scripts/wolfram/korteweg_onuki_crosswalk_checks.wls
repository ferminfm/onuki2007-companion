(* Blackboard-level finite Cartesian trace for the bounded Korteweg--Onuki
   local-stress crosswalk. The trace does not prove a continuum PDE, global
   balance, constitutive law, historical influence, or numerical branch. *)

ClearAll["Global`*"];
failures = {};
traceRows = {};
summaryRows = {};

reduceResidual[residual_] := FullSimplify[Expand[If[MatrixQ[residual],
  Total[Flatten[residual]^2], residual]]];

recordStep[id_String, anchor_String, premise_String, input_,
    transformation_String, assumptions_String, output_, residual_,
    expected_String] := Module[{reduced, status},
  reduced = reduceResidual[residual];
  status = Which[
    expected === "ZERO" && TrueQ[reduced === 0], "PASS_ZERO",
    expected === "NONZERO" && ! TrueQ[reduced === 0],
      "PASS_EXPECTED_NONZERO",
    True, "FAIL"
  ];
  AppendTo[traceRows, {
    id, anchor, premise, ToString[input, InputForm], transformation,
    assumptions, ToString[output, InputForm], ToString[reduced, InputForm],
    status
  }];
  AppendTo[summaryRows, {id, ToString[reduced, InputForm], status}];
  Print[id <> "\t" <> status <> "\t" <> ToString[reduced, InputForm]];
  If[status === "FAIL", AppendTo[failures, {id, reduced, expected}]];
];

g = {nx, ny};
h = {{nxx, nxy}, {nxy, nyy}};
q = g.g;
lap = nxx + nyy;
mixed = nx tx + ny ty;
id2 = IdentityMatrix[2];

alphaN = -(mCoeff + n mN)/2;
betaN = mCoeff;
gammaN = mCoeff n;
kMapped = (alphaN q - gammaN lap) id2 + betaN Outer[Times, g, g];

rhoG = mass g;
rhoH = mass h;
rhoLap = mass lap;
kMass = ((alphaN/mass^2) (rhoG.rhoG) -
    (gammaN/mass) rhoLap) id2 +
  (betaN/mass^2) Outer[Times, rhoG, rhoG] - 0 rhoH;
recordStep["KO01", "Korteweg Eq. (20), p. 12; rho=m_0 n",
  "Rewrite mass-density derivatives and coefficients in number density",
  kMass, "Substitute rho_i=m_0 n_i, rho_ij=m_0 n_ij and the coefficient map",
  "constant nonzero m_0; delta_K=0", kMapped, kMass - kMapped, "ZERO"];

(* Onuki Eq. (2.48): M_n is the n derivative at fixed T and M_T is the
   T derivative at fixed n. The spatial chain rule is applied before the
   constitutive relation M=C T+K is imposed. *)
sourceP1 = ((n mN - mCoeff)/2) q - mCoeff n lap -
  temp n (mN q/temp + (mT/temp - mCoeff/temp^2) mixed);
expandedP1 = -(mCoeff + n mN) q/2 - mCoeff n lap +
  n (mCoeff/temp - mT) mixed;
recordStep["KO02", "Onuki Eq. (2.48), PRE p. 4",
  "Expand -T n grad n . grad(M/T) with thermodynamic partial derivatives",
  sourceP1, "Distribute and collect q, Laplacian, and grad n . grad T terms",
  "M=M(n,T); M_n at fixed T; M_T at fixed n; T nonzero", expandedP1,
  sourceP1 - expandedP1, "ZERO"];

constitutiveP1 = alphaN q - gammaN lap + (n kCoeff/temp) mixed;
recordStep["KO03", "KO02; M=C T+K",
  "Use M_T=C and M/T-M_T=K/T",
  expandedP1, "Substitute M=C T+K and M_T=C, then collect",
  "C=C(n); K=K(n); T nonzero", constitutiveP1,
  (expandedP1 - constitutiveP1) /.
    {mCoeff -> cCoeff temp + kCoeff, mT -> cCoeff}, "ZERO"];

onukiGeneral = constitutiveP1 id2 + mCoeff Outer[Times, g, g];
expectedMixed = (n kCoeff/temp) mixed id2;
recordStep["KO04", "KO01 and KO03",
  "Compare the two local pressure-positive capillary tensors",
  onukiGeneral - kMapped, "Subtract after the coefficient and density maps",
  "same Cartesian frame and pressure-positive convention", expectedMixed,
  (onukiGeneral - kMapped) - expectedMixed, "ZERO"];

recordStep["KO05", "KO04",
  "The mixed residual vanishes in an isothermal field",
  onukiGeneral - kMapped, "Set grad T=0",
  "tx=ty=0", ConstantArray[0, {2, 2}],
  (onukiGeneral - kMapped) /. {tx -> 0, ty -> 0}, "ZERO"];

recordStep["KO06", "KO04",
  "The mixed residual vanishes for K=0 even when grad T is nonzero",
  onukiGeneral - kMapped, "Set K=0",
  "kCoeff=0", ConstantArray[0, {2, 2}],
  (onukiGeneral - kMapped) /. kCoeff -> 0, "ZERO"];

recordStep["KO07", "KO06; Onuki simulation specialization",
  "Constant C additionally gives M_n=0 without changing the zero residual",
  onukiGeneral - kMapped, "Set K=0 and M_n=0",
  "K=0; C constant; no inference about unpublished code",
  ConstantArray[0, {2, 2}],
  (onukiGeneral - kMapped) /. {kCoeff -> 0, mN -> 0}, "ZERO"];

hessianResidual = -mass deltaSource h;
recordStep["KO08", "Korteweg Eq. (20), p. 12",
  "Retain Korteweg's independent Hessian coefficient",
  hessianResidual[[1, 2]], "Compare with the mapped Onuki slice delta_K=0",
  "nonzero deltaSource and mixed Hessian component", 0,
  hessianResidual[[1, 2]], "NONZERO"];

nPoly = 1 + x^2;
tPoly = 2 + x;
scalarResidual = (3 nPoly/tPoly) D[nPoly, x] D[tPoly, x];
forceResidual = D[scalarResidual, x];
recordStep["KO09", "KO04",
  "A nonzero scalar tensor residual generally changes its divergence",
  scalarResidual, "Differentiate a one-dimensional polynomial witness",
  "n=1+x^2; T=2+x; K=3", 0, forceResidual, "NONZERO"];

wrongSignWitness = 2 D[(alphaN q - gammaN lap) /.
  {nx -> x, ny -> x^2, nxx -> 1, nyy -> 2}, x];
recordStep["KO10", "Korteweg Eq. (1), p. 1",
  "Using the opposite pressure-stress sign changes the force",
  wrongSignWitness, "Evaluate a nontrivial polynomial witness",
  "pressure-positive tensors compared directly", 0, wrongSignWitness,
  "NONZERO"];

scalarGaugeWitness = D[x^3, x];
recordStep["KO11", "Modern pressure-gauge guardrail",
  "A scalar tensor shift is not force-neutral without a pressure map",
  x^3 id2, "Take the one-dimensional divergence",
  "equation-of-state and boundary data not supplied", 0,
  scalarGaugeWitness, "NONZERO"];

projectRoot = Nest[DirectoryName, $InputFileName, 3];
generatedDir = FileNameJoin[{projectRoot, "generated", "wolfram"}];
If[! DirectoryQ[generatedDir],
  CreateDirectory[generatedDir, CreateIntermediateDirectories -> True]];

traceHeaders = {"trace_id", "anchor", "premise", "input",
  "transformation", "assumptions", "output", "residual", "status"};
Export[FileNameJoin[{generatedDir, "korteweg_onuki_crosswalk_trace.tsv"}],
  Prepend[traceRows, traceHeaders], "TSV"];
Export[FileNameJoin[{generatedDir, "korteweg_onuki_crosswalk_summary.tsv"}],
  Prepend[summaryRows, {"check_id", "residual", "status"}], "TSV"];
markdown = "# Korteweg--Onuki crosswalk trace\n\n" <>
  StringRiffle[("- `" <> #[[1]] <> "` " <> #[[9]] <>
    ": residual `" <> #[[8]] <> "`") & /@ traceRows, "\n"] <> "\n";
Export[FileNameJoin[{generatedDir, "korteweg_onuki_crosswalk_trace.md"}],
  markdown, "Text"];

If[Length[failures] > 0,
  Print["FAIL: Korteweg--Onuki crosswalk Wolfram trace"];
  Print[failures // InputForm];
  Exit[1],
  Print["PASS: Korteweg--Onuki crosswalk Wolfram trace"];
  Exit[0]
];
