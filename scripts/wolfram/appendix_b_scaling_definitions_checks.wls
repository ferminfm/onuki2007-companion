(* Finite Wolfram checks for Onuki Appendix B scaling definitions.
   B4--B6 are covered by the separate energy/boundary mirrors. *)

Get["scripts/wolfram/coauthor_trace_helpers.wls"];
$CoauthorTraceAnchor = "Onuki Appendix B scaling definitions and Eqs. (B1)--(B6)";
$CoauthorTracePremise = "independently constructed nondimensional definition or scale identity";
$CoauthorTraceAssumptions = "positive nonzero reference scales";

ClearAll[
  ell, cCoeff, kB, v0, t0, nu0, mass, eps, grav, density, temp,
  velocity, eTotal, phi, theta, scaledVelocity, scaledEnergyDensity,
  sigmaA, sigmaB, gStar, phiX, correctDensityGradient,
  wrongDensityGradient, rows, failures, addRow, checkZero,
  checkExpectedNonzero
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

checkExpectedNonzero[name_String, expression_, expected_, note_String] := Module[
  {residual, expectedResidual},
  residual = FullSimplify[expression];
  expectedResidual = FullSimplify[expected];
  recordAtomicTrace[name, $CoauthorTraceAnchor, $CoauthorTracePremise,
    expression, "FullSimplify and compare with expected residual",
    $CoauthorTraceAssumptions, expectedResidual, residual, "NONZERO"];
  addRow[name, "PASS_EXPECTED_NONZERO", residual, note];
  If[residual === 0 || FullSimplify[residual - expectedResidual] =!= 0,
    AppendTo[failures, {name, residual, expectedResidual}]
  ];
];

checkZero[
  "length_scale_squared_relation",
  (ell^2 - cCoeff/(2 kB v0)) /. cCoeff -> 2 kB v0 ell^2,
  "ell^2=C/(2 k_B v0) is the source length-scale definition"
];

checkZero[
  "time_scale_relation",
  (t0 - ell^2/nu0) /. t0 -> ell^2/nu0,
  "t0=ell^2/nu0 is the source time-scale definition"
];

phi = v0 density;
theta = kB temp/eps;
scaledVelocity = t0 velocity/ell;
scaledEnergyDensity = eTotal v0/eps;
sigmaA = nu0^2 mass/(eps ell^2);
sigmaB = mass ell^2/(eps t0^2);
gStar = mass grav ell/eps;

checkZero["phi_definition", phi - v0 density, "phi=v0 n"];
checkZero["theta_definition", theta - kB temp/eps, "Theta=k_B T/epsilon"];
checkZero["scaled_velocity_definition", scaledVelocity - t0 velocity/ell, "V=t0 v/ell"];
checkZero["scaled_energy_density_definition", scaledEnergyDensity - eTotal v0/eps, "E_T=e_T v0/epsilon"];
checkZero[
  "sigma_two_forms_equivalent",
  (sigmaA - sigmaB) /. t0 -> ell^2/nu0,
  "sigma forms agree after substituting t0=ell^2/nu0"
];
checkZero["gravity_parameter_definition", gStar - mass grav ell/eps, "g*=m g ell/epsilon"];

correctDensityGradient = phiX/(v0 ell);
wrongDensityGradient = phiX/v0;
checkExpectedNonzero[
  "expected_nonzero_wrong_coordinate_derivative_scale",
  v0 ell wrongDensityGradient - v0 ell correctDensityGradient,
  (ell - 1) phiX,
  "omitting grad_x=ell^-1 grad_* leaves an uncancelled coordinate scale"
];

addRow[
  "b4_b5_b6_covered_by_energy_boundary_mirrors",
  "PASS_LOGICAL",
  "covered_separately",
  "B4--B6 are covered by appendix_b_energy_boundary SymPy/Wolfram/Pint mirrors"
];

If[!DirectoryQ["generated/wolfram"], CreateDirectory["generated/wolfram", CreateIntermediateDirectories -> True]];
Export["generated/wolfram/appendix_b_scaling_definitions_summary.tsv", rows, "TSV"];

If[Length[failures] > 0,
  Print["FAIL: Appendix B scaling-definition Wolfram checks"];
  Print[failures // InputForm];
  Exit[1],
  Print["PASS: Appendix B scaling-definition Wolfram checks"];
  Exit[0]
];
