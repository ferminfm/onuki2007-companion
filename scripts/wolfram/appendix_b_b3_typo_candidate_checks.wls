(* Focused Wolfram checks for the Appendix-B B3 diagonal factor.
   These checks support the dimensional-source scaling branch only. They do not
   establish an official erratum, author intent, unpublished implementation
   behavior, numerical impact, or PDE well-posedness. *)

Get["scripts/wolfram/coauthor_trace_helpers.wls"];
$CoauthorTraceAnchor = "Onuki Eq. (B3) dimensional-source and printed branches";
$CoauthorTracePremise = "independently constructed diagonal scaling and branch residual";
$CoauthorTraceAssumptions = "Appendix-B scales; no unpublished-code assumption";

ClearAll[Cc, kB, v0, ell, eps, theta, phi, lapPhi, gradPhiSq,
  phiI, phiJ, x, theta0, failures, checkZero, checkExpectedNonzero];

failures = {};

checkZero[name_String, expression_, note_String] := Module[{residual},
  residual = FullSimplify[expression];
  recordAtomicTrace[name, $CoauthorTraceAnchor, $CoauthorTracePremise,
    expression, "FullSimplify", $CoauthorTraceAssumptions, 0, residual,
    "ZERO"];
  Print[name <> "\tPASS_ZERO\t" <> ToString[residual, InputForm] <> "\t" <> note];
  If[residual =!= 0, AppendTo[failures, {name, residual}]];
];

checkExpectedNonzero[name_String, expression_, expected_, note_String] := Module[
  {residual, expectedResidual},
  residual = FullSimplify[expression];
  expectedResidual = FullSimplify[expected];
  recordAtomicTrace[name, $CoauthorTraceAnchor, $CoauthorTracePremise,
    expression, "FullSimplify and compare with expected residual",
    $CoauthorTraceAssumptions, expectedResidual, residual, "NONZERO"];
  Print[name <> "\tPASS_EXPECTED_NONZERO\t" <> ToString[residual, InputForm] <> "\t" <> note];
  If[residual === 0, AppendTo[failures, {name, "unexpected zero"}]];
  If[FullSimplify[residual - expectedResidual] =!= 0,
    AppendTo[failures, {name, residual, expectedResidual}]
  ];
];

M = Cc eps theta/kB;
cToEllRule = Cc -> 2 kB v0 ell^2;

checkZero[
  "M_scales_to_two_epsilon_v0_ell_squared_theta",
  (M /. Cc -> 2 kB v0 ell^2) - 2 eps v0 ell^2 theta,
  "M=CT with Theta=kB T/epsilon and ell^2=C/(2 kB v0)"
];

lapXN = lapPhi/(v0 ell^2);
gradXNSq = gradPhiSq/(v0^2 ell^2);
gradIN = phiI/(v0 ell);
gradJN = phiJ/(v0 ell);
nField = phi/v0;

scaledLapTerm = (v0/eps) (-M nField lapXN);
checkZero[
  "diagonal_laplacian_scales_to_minus_two_theta_phi_lap_phi",
  (scaledLapTerm /. cToEllRule) + 2 theta phi lapPhi,
  "scaling of -M n Delta_x n retains the phi factor"
];

scaledGradSquare = (v0/eps) (-(M/2) gradXNSq);
checkZero[
  "gradient_square_scales_to_minus_theta_grad_phi_squared",
  (scaledGradSquare /. cToEllRule) + theta gradPhiSq,
  "scaling of -(M/2)|grad_x n|^2"
];

scaledOffdiag = (v0/eps) M gradIN gradJN;
checkZero[
  "offdiagonal_gradient_stress_scales_to_two_theta_phi_i_phi_j",
  (scaledOffdiag /. cToEllRule) - 2 theta phiI phiJ,
  "scaling of M partial_i n partial_j n"
];

sourceDiagLap = -2 theta phi lapPhi;
printedDiagLap = -2 theta lapPhi;
expectedStressResidual = 2 theta (phi - 1) lapPhi;
checkExpectedNonzero[
  "printed_minus_source_diagonal_laplacian_residual",
  printedDiagLap - sourceDiagLap,
  expectedStressResidual,
  "printed branch lacks the dimensional-source phi factor"
];

phiTest = 1 + x^2;
stressResidual1D = 2 theta0 (phiTest - 1) D[phiTest, {x, 2}];
forceResidual1D = -D[stressResidual1D, x];
checkExpectedNonzero[
  "one_dimensional_force_residual_generically_nonzero",
  forceResidual1D,
  -8 theta0 x,
  "for phi(x)=1+x^2, -d_x[2 Theta (phi-1) phi_xx] is nonzero"
];

wrongScaledLap = (v0/eps) (-M lapXN);
wrongResult = FullSimplify[wrongScaledLap /. cToEllRule];
Print["negative_control_replace_n_lap_n_by_lap_n\tNEGATIVE_CONTROL_NOT_SOURCE_GROUNDED\t" <>
  ToString[wrongResult, InputForm] <>
  "\treplacing n Delta n by Delta n leaves a v0-dependent object and is not the source term"];
If[FullSimplify[wrongResult + 2 theta lapPhi] === 0,
  AppendTo[failures, {"negative_control_replace_n_lap_n_by_lap_n", wrongResult}]
];

Print["unpublished_simulation_code_branch_regression\tPASS_LOGICAL\tUNRESOLVED_SOURCE_DEPENDENT\tunpublished implementation branch is not inferred"];

If[Length[failures] > 0,
  Print["FAIL: Appendix B B3 typo-candidate Wolfram checks"];
  Print[failures // InputForm];
  Exit[1],
  Print["PASS: Appendix B B3 typo-candidate Wolfram checks"];
  Exit[0]
];
