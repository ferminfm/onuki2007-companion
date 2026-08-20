(* Finite Wolfram checks for Onuki Appendix B momentum/B3 branches.
   These checks verify algebraic scaling and branch residuals only. *)

Get["scripts/wolfram/coauthor_trace_helpers.wls"];
$CoauthorTraceAnchor = "Onuki Eq. (B3) from Eqs. (2.47)--(2.48)";
$CoauthorTracePremise = "independently constructed dimensional-to-scaled pressure-tensor component";
$CoauthorTraceAssumptions = "Appendix-B scales; source and printed branches kept separate";

ClearAll[m, ell, eps, t0, nu0, g, phi, theta, lapPhi,
  gradPhiSq, p0, cCoeff, kB, v0, phiI, phiJ, phiX, phiXX, phiXXX,
  failures, checkZero, checkExpectedNonzero];

failures = {};

checkZero[name_String, expression_] := Module[{residual},
  residual = FullSimplify[expression];
  recordAtomicTrace[name, $CoauthorTraceAnchor, $CoauthorTracePremise,
    expression, "FullSimplify", $CoauthorTraceAssumptions, 0, residual,
    "ZERO"];
  Print[name <> "\tPASS_ZERO\t" <> ToString[residual, InputForm]];
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
  If[residual === 0, AppendTo[failures, {name, "unexpected zero"}]];
  If[FullSimplify[residual - expectedResidual] =!= 0,
    AppendTo[failures, {name, residual, expectedResidual}]
  ];
];

checkZero[
  "sigma_two_forms_in_momentum_scaling",
  (m ell^2/(eps t0^2) /. t0 -> ell^2/nu0) -
    (nu0^2 m/(eps ell^2))
];

checkZero[
  "gravity_scale_definition",
  m g ell/eps - m g ell/eps
];

coeff = ((v0/eps) (cCoeff eps theta/kB)/(v0^2 ell^2)) /.
  cCoeff -> 2 kB v0 ell^2;

checkZero[
  "gradient_stress_coefficient_scales_to_two_theta",
  coeff - 2 theta
];

checkZero[
  "diagonal_gradient_square_coefficient_scales_to_theta",
  coeff/2 - theta
];

sourceDiag = p0 - theta gradPhiSq - 2 theta phi lapPhi;
printedDiag = p0 - theta gradPhiSq - 2 theta lapPhi;
expectedResidual = 2 theta (phi - 1) lapPhi;

checkExpectedNonzero[
  "printed_minus_dimensional_source_b3_residual",
  printedDiag - sourceDiag,
  expectedResidual
];

checkZero[
  "offdiagonal_gradient_stress_same_in_both_branches",
  2 theta phiI phiJ - 2 theta phiI phiJ
];

viscCoeff = (v0/eps) (nu0 m phi/v0) (1/t0);
sigmaDef = m ell^2/(eps t0^2);

checkZero[
  "viscous_stress_coefficient_scales_to_sigma_phi",
  (viscCoeff /. t0 -> ell^2/nu0) -
    (sigmaDef phi /. t0 -> ell^2/nu0)
];

residual1D = 2 theta (phi - 1) phiXX;
derivative1D = 2 theta ((phi - 1) phiXXX + phiX phiXX);
chainDerivative = D[residual1D, phi] phiX + D[residual1D, phiXX] phiXXX;

checkZero[
  "one_dimensional_constant_theta_branch_residual_derivative",
  derivative1D - chainDerivative
];

If[Length[failures] > 0,
  Print["FAIL: Appendix B momentum/B3 Wolfram checks"];
  Print[failures // InputForm];
  Exit[1],
  Print["PASS: Appendix B momentum/B3 Wolfram checks"];
  Exit[0]
];
