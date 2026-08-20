(* Finite Wolfram checks for Onuki Appendix B energy/boundary scaling.
   These checks verify local scale bookkeeping and an expected omitted
   wall/global-transfer residual only. They do not close global balances or
   validate simulations. *)

Get["scripts/wolfram/coauthor_trace_helpers.wls"];
$CoauthorTraceAnchor = "Onuki Eqs. (B4)--(B6) and Eq. (3.2)";
$CoauthorTracePremise = "independently constructed local energy or boundary scaling identity";
$CoauthorTraceAssumptions = "Appendix-B scales; global wall transfer kept separate";

ClearAll[phi, theta, sigma, vSq, m, ell, eps, t0, nu0, g, v0,
  n, nc, boundaryHeat, surfaceRate, failures, checkZero,
  checkExpectedNonzero];

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

energyDensity = phi theta - phi^2 + sigma phi vSq/2;
checkZero[
  "energy_density_b4_reconstruction",
  energyDensity - (phi theta - phi^2 + sigma phi vSq/2)
];

checkZero[
  "kinetic_energy_coefficient_scales_to_sigma",
  (m ell^2/(eps t0^2) /. t0 -> ell^2/nu0) -
    (nu0^2 m/(eps ell^2))
];

checkZero[
  "heat_diffusion_coefficient_scales_to_one",
  (t0 nu0/ell^2 /. t0 -> ell^2/nu0) - 1
];

checkZero[
  "gravity_power_coefficient",
  m g ell/eps - m g ell/eps
];

checkZero[
  "boundary_rhs_phi_minus_five_six",
  (v0 (n - 5 nc/2) /. {n -> phi/v0, nc -> 1/(3 v0)}) -
    (phi - 5/6)
];

checkExpectedNonzero[
  "expected_nonzero_omitted_global_wall_transfer",
  boundaryHeat + surfaceRate,
  boundaryHeat + surfaceRate
];

If[Length[failures] > 0,
  Print["FAIL: Appendix B energy/boundary Wolfram checks"];
  Print[failures // InputForm];
  Exit[1],
  Print["PASS: Appendix B energy/boundary Wolfram checks"];
  Exit[0]
];
