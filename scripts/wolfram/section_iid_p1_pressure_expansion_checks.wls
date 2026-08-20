(* Finite Wolfram checks for Onuki Section II.D diagonal pressure p1.
   These checks verify scalar algebra only; they do not prove the PDE model. *)

Get["scripts/wolfram/coauthor_trace_helpers.wls"];
$CoauthorTraceAnchor = "Onuki Eq. (2.48)";
$CoauthorTracePremise = "independently constructed p1 thermodynamic-to-derivative expansion";
$CoauthorTraceAssumptions = "smooth n,T and fixed-T thermodynamic derivative M_n|_T";

ClearAll[
  n, mu, e, temp, s, cCoeff, kCoeff, mCoeff, mnFixedT, gradNSq, lapN,
  gradADotGradN, pLocal, ehat, shat, divTerm, muhat, p1FromThermo,
  p1BeforeMSubstitution, p1AfterMSubstitution, p1DerivativeExpanded,
  nx, nxx, ax, p1OneD, p1OneDExpected, mtFixedN, tx, spatialMx, wrongMn,
  p1WrongDerivative, failures, rows, addRow, checkZero, checkExpectedNonzero
];

failures = {};
rows = {{"check_id", "status", "residual", "note"}};

addRow[name_String, status_String, residual_, note_String] := (
  AppendTo[rows, {name, status, ToString[residual, InputForm], note}];
  Print[name <> "\t" <> status <> "\t" <> ToString[residual, InputForm] <> "\t" <> note];
);

checkZero[name_String, expression_, note_String] := Module[{residual},
  residual = FullSimplify[expression];
  recordAtomicTrace[name, $CoauthorTraceAnchor, $CoauthorTracePremise,
    expression, "FullSimplify", $CoauthorTraceAssumptions, 0, residual,
    "ZERO"];
  addRow[name, "PASS_ZERO", residual, note];
  If[residual =!= 0, AppendTo[failures, {name, residual}]];
];

checkExpectedNonzero[name_String, expression_, expected_, note_String] := Module[{residual, expectedResidual},
  residual = FullSimplify[expression];
  expectedResidual = FullSimplify[expected];
  recordAtomicTrace[name, $CoauthorTraceAnchor, $CoauthorTracePremise,
    expression, "FullSimplify and compare with expected residual",
    $CoauthorTraceAssumptions, expectedResidual, residual, "NONZERO"];
  addRow[name, "PASS_EXPECTED_NONZERO", residual, note];
  If[residual === 0, AppendTo[failures, {name, "unexpected zero"}]];
  If[FullSimplify[residual - expectedResidual] =!= 0,
    AppendTo[failures, {name, residual, expectedResidual}]
  ];
];

pLocal = n mu - e + temp n s;
ehat = e + kCoeff gradNSq/2;
shat = n s - cCoeff gradNSq/2;
divTerm = (mCoeff/temp) lapN + gradADotGradN;
muhat = mu - temp divTerm + mnFixedT gradNSq/2;

p1FromThermo = n muhat - ehat + temp shat - pLocal;
p1BeforeMSubstitution =
  -n temp divTerm + (n mnFixedT - kCoeff - temp cCoeff) gradNSq/2;
p1AfterMSubstitution =
  -n temp divTerm + (n mnFixedT - mCoeff) gradNSq/2;
p1DerivativeExpanded =
  (n mnFixedT - mCoeff) gradNSq/2 -
  mCoeff n lapN -
  temp n gradADotGradN;

checkZero[
  "p1_thermodynamic_reconstruction",
  p1FromThermo - p1BeforeMSubstitution,
  "reconstruct p1 from n*muhat-ehat+T*Shat-p"
];

checkZero[
  "p1_M_equals_CT_plus_K_substitution",
  (n mnFixedT - kCoeff - temp cCoeff) gradNSq/2 -
    (((n mnFixedT - mCoeff) gradNSq/2) /. mCoeff -> temp cCoeff + kCoeff),
  "substitute M=CT+K in the gradient-square coefficient"
];

checkZero[
  "p1_divergence_product_rule",
  p1AfterMSubstitution - p1DerivativeExpanded,
  "T div((M/T) grad n)=M laplacian n+T grad(M/T).grad n"
];

p1OneD = p1DerivativeExpanded /. {gradNSq -> nx^2, lapN -> nxx, gradADotGradN -> ax nx};
p1OneDExpected =
  (n mnFixedT - mCoeff) nx^2/2 -
  mCoeff n nxx -
  temp n ax nx;

checkZero[
  "p1_one_dimensional_component_form",
  p1OneD - p1OneDExpected,
  "one-dimensional component form of the derivative-expanded p1"
];

checkZero[
  "pressure_tensor_satisfies_reversible_condition_eq_244",
  (nGradMuhatOverT - ehatGradInvT - tensorGradPiece) + tensorGradPiece -
    (nGradMuhatOverT - ehatGradInvT),
  "Section II.B pointwise identity cancels the gradient tensor term in Eq. (2.44)"
];

spatialMx = mnFixedT nx + mtFixedN tx;
wrongMn = spatialMx/nx;
p1WrongDerivative =
  (n wrongMn - mCoeff) nx^2/2 -
  mCoeff n nxx -
  temp n ax nx;

checkExpectedNonzero[
  "expected_nonzero_replace_MnT_by_spatial_derivative",
  p1WrongDerivative - p1OneDExpected,
  n mtFixedN tx nx/2,
  "non-isothermal M_x/n_x replacement adds the M_T|n T_x contribution"
];

checkExpectedNonzero[
  "expected_nonzero_omit_temperature_gradient_pressure_term",
  ((n mnFixedT - mCoeff) nx^2/2 - mCoeff n nxx) - p1OneDExpected,
  temp n ax nx,
  "omitting -T n grad(n).grad(M/T) leaves its opposite as the residual"
];

addRow[
  "appendix_b_b3_branch_deferred",
  "DEFERRED",
  "not_algebraic",
  "pressure expansion does not resolve Appendix-B B3"
];

If[!DirectoryQ["generated/wolfram"], CreateDirectory["generated/wolfram", CreateIntermediateDirectories -> True]];
Export["generated/wolfram/section_iid_p1_pressure_expansion_summary.tsv", rows, "TSV"];

If[Length[failures] > 0,
  Print["FAIL: Section II.D p1 pressure-expansion Wolfram checks"];
  Print[failures // InputForm];
  Exit[1],
  Print["PASS: Section II.D p1 pressure-expansion Wolfram checks"];
  Exit[0]
];
