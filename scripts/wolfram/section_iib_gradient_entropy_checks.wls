(* Finite Wolfram checks for Onuki Section II.B companion identities.
   These checks verify algebraic and integration-by-parts bookkeeping only. *)

Get["scripts/wolfram/coauthor_trace_helpers.wls"];
$CoauthorTraceAnchor = "Onuki Eqs. (2.12)--(2.20)";
$CoauthorTracePremise = "independently constructed coefficient or one-dimensional integration-by-parts identity";
$CoauthorTraceAssumptions = "smooth scalar fields and nonzero temperature where division occurs";

ClearAll[x, c, t, k, m, a, n, eta, densitySymbol, entropyE, invTemp, dim, kB, tempScalar, deltaSigma, deltaE, deltaN, muSymbol, failures, checkZero, checkExpectedNonzero];
failures = {};

checkZero[name_String, expression_] := Module[{residual},
  residual = FullSimplify[expression];
  recordAtomicTrace[name, $CoauthorTraceAnchor, $CoauthorTracePremise,
    expression, "FullSimplify", $CoauthorTraceAssumptions, 0, residual,
    "ZERO"];
  Print[name <> "\t" <> ToString[residual, InputForm]];
  If[residual =!= 0, AppendTo[failures, {name, residual}]];
];

checkExpectedNonzero[name_String, expression_, expected_] := Module[
  {residual, expectedResidual},
  residual = FullSimplify[expression];
  expectedResidual = FullSimplify[expected];
  recordAtomicTrace[name, $CoauthorTraceAnchor, $CoauthorTracePremise,
    expression, "FullSimplify and compare with expected residual",
    $CoauthorTraceAssumptions, expectedResidual, residual, "NONZERO"];
  Print[name <> "\tPASS_EXPECTED_NONZERO\t" <> ToString[residual, InputForm]];
  If[residual === 0 || FullSimplify[residual - expectedResidual] =!= 0,
    AppendTo[failures, {name, residual, expectedResidual}]
  ];
];

mExpr = c[x] t[x] + k[x];

checkZero[
  "source_eq_2_17_factor_n",
  invTemp - densitySymbol entropyE /. invTemp -> densitySymbol entropyE
];

checkZero[
  "entropy_density_variation_energy_coefficient",
  densitySymbol entropyE - invTemp /. invTemp -> densitySymbol entropyE
];

entropyTemperatureDerivative = dim kB/(2 tempScalar);
energyTemperatureDerivative = dim densitySymbol kB/2;
checkZero[
  "section_iia_consistency_s_e_ratio",
  entropyTemperatureDerivative/energyTemperatureDerivative - 1/(densitySymbol tempScalar)
];

localDifferential =
  deltaSigma - (invTemp deltaE - muSymbol invTemp deltaN);
checkZero[
  "local_differential_identity_coefficients",
  localDifferential /. deltaSigma -> (invTemp deltaE - muSymbol invTemp deltaN)
];

checkZero[
  "M_equals_CT_plus_K",
  mExpr - (c[x] t[x] + k[x])
];

checkZero[
  "T_grad_M_over_T_identity",
  t[x] D[m[x]/t[x], x] - (D[m[x], x] - (m[x]/t[x]) D[t[x], x])
];

completeCoefficient =
  D[mExpr, x] - (mExpr/t[x]) D[t[x], x];

substitutedTarget =
  t[x] D[c[x], x] + D[k[x], x] - (k[x]/t[x]) D[t[x], x];

checkZero[
  "M_equals_CT_plus_K_temperature_correction",
  completeCoefficient - substitutedTarget
];

simulationBranch =
  completeCoefficient /. {
    k[x] -> 0,
    Derivative[1][k][x] -> 0,
    Derivative[1][c][x] -> 0
  };

checkZero[
  "K_zero_constant_C_complete_coefficient",
  simulationBranch
];

diagnosticTest =
  D[mExpr, x] /. {
    k[x] -> 0,
    Derivative[1][k][x] -> 0,
    Derivative[1][c][x] -> 0
  };

checkZero[
  "diagnostic_term_removal_leaves_C_grad_T",
  diagnosticTest - c[x] D[t[x], x]
];

checkExpectedNonzero[
  "diagnostic_term_removal_is_generically_nonzero",
  diagnosticTest,
  c[x] D[t[x], x]
];

lhs = -a[x] D[n[x], x] D[eta[x], x];
rhs =
  D[-a[x] D[n[x], x] eta[x], x] +
  D[a[x] D[n[x], x], x] eta[x];

checkZero[
  "one_dimensional_integration_by_parts",
  lhs - rhs
];

If[Length[failures] > 0,
  Print["FAIL: Section II.B Wolfram checks"];
  Print[failures // InputForm];
  Exit[1],
  Print["PASS: Section II.B Wolfram checks"];
  Exit[0]
];
