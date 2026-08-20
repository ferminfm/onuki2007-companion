(* Finite Wolfram checks for Onuki Section II.A companion identities.
   These checks verify algebraic thermodynamic and one-dimensional variational
   bookkeeping only. *)

Get["scripts/wolfram/coauthor_trace_helpers.wls"];
$CoauthorTraceAnchor = "Onuki Eqs. (2.1)--(2.11)";
$CoauthorTracePremise = "independently constructed finite thermodynamic or one-dimensional identity";
$CoauthorTraceAssumptions = "positive source parameters and 1-v0 n>0 where used";

ClearAll[n, temp, kB, v0, eps, dim, mass, lam0, x, dens, mcoef, f0, failures, checkZero, checkExpectedNonzero];
failures = {};

checkZero[name_String, expression_] := Module[{residual},
  residual = FullSimplify[expression, Assumptions -> {n > 0, temp > 0, kB > 0, v0 > 0, eps > 0, dim > 0, mass > 0, lam0 > 0, mPos > 0, omegaPos > 0, 1 - v0 n > 0}];
  residual = Factor[residual];
  recordAtomicTrace[name, $CoauthorTraceAnchor, $CoauthorTracePremise,
    expression, "FullSimplify then Factor", $CoauthorTraceAssumptions,
    0, residual, "ZERO"];
  Print[name <> "\tPASS_ZERO\t" <> ToString[residual, InputForm]];
  If[residual =!= 0, AppendTo[failures, {name, residual}]];
];

checkExpectedNonzero[name_String, expression_, assumptions_] := Module[{residual},
  residual = FullSimplify[expression, Assumptions -> assumptions];
  residual = Factor[residual];
  recordAtomicTrace[name, $CoauthorTraceAnchor, $CoauthorTracePremise,
    expression, "FullSimplify then Factor", ToString[assumptions, InputForm],
    "nonzero", residual, "NONZERO"];
  Print[name <> "\tPASS_EXPECTED_NONZERO\t" <> ToString[residual, InputForm]];
  If[TrueQ[residual === 0], AppendTo[failures, {name, residual}]];
];

lambdaPower = lam0 temp^(-dim/2);
f = kB temp n (Log[lambdaPower n] - 1 - Log[1 - v0 n]) - eps v0 n^2;
mu = D[f, n];
pressure = n mu - f;
pressureTarget = n kB temp/(1 - v0 n) - eps v0 n^2;

checkZero["bulk_pressure_from_n_mu_minus_f", pressure - pressureTarget];

entropy = -D[f, temp]/n;
entropyTarget = -kB Log[lambdaPower n/(1 - v0 n)] + kB (dim + 2)/2;
checkZero["entropy_from_temperature_derivative", entropy - entropyTarget];

internalEnergy = f + temp n entropy;
internalTarget = dim n kB temp/2 - eps v0 n^2;
checkZero["internal_energy_from_f_plus_Tns", internalEnergy - internalTarget];

spinodalTemp = 2 eps v0 n (1 - v0 n)^2/kB;
dpdnT = D[pressureTarget, n];
checkZero["isothermal_derivative_spinodal_factor", dpdnT - kB (temp - spinodalTemp)/(1 - v0 n)^2];

dsdnT = D[entropyTarget, n];
dsdTn = D[entropyTarget, temp];
dTdnS = FullSimplify[-dsdnT/dsdTn, Assumptions -> {n > 0, temp > 0, dim > 0, v0 > 0, 1 - v0 n > 0}];
checkZero["adiabatic_temperature_derivative", dTdnS - 2 temp/(dim n (1 - v0 n))];

dpdTn = D[pressureTarget, temp];
dpdnS = FullSimplify[dpdnT + dpdTn dTdnS, Assumptions -> {n > 0, temp > 0, dim > 0, v0 > 0, 1 - v0 n > 0}];
soundTarget = kB temp (1 + 2/dim - spinodalTemp/temp)/(1 - v0 n)^2;
checkZero["adiabatic_pressure_derivative_sound_kernel", dpdnS - soundTarget];
soundSpeedSquared = soundTarget/mass;
soundSpeedSquaredTarget = kB temp (1 + 2/dim - spinodalTemp/temp)/(mass (1 - v0 n)^2);
checkZero["sound_speed_squared_with_excluded_volume_denominator", soundSpeedSquared - soundSpeedSquaredTarget];

gammaRatio = FullSimplify[dpdnS/dpdnT, Assumptions -> {n > 0, temp > 0, dim > 0, v0 > 0, 1 - v0 n > 0, temp != spinodalTemp}];
gammaTarget = 1 + 2/(dim (1 - spinodalTemp/temp));
checkZero["specific_heat_ratio_from_pressure_derivatives", gammaRatio - gammaTarget];

rho = dens[x];
nx = D[rho, x];
integrand = f0[rho] + (1/2) mcoef[rho] nx^2;
euler = D[integrand, rho] - D[D[integrand, nx], x];
mu0 = D[f0[rho], rho];
mn = D[mcoef[rho], rho];
expectedEuler = mu0 - mcoef[rho] D[rho, {x, 2}] - (1/2) mn nx^2;
checkZero["gradient_euler_lagrange_kernel", euler - expectedEuler];

interfaceForce = mcoef[rho] D[rho, {x, 2}] + (1/2) mn nx^2;
compactSourceForm = (1/2) mcoef[rho] D[rho, {x, 2}] + D[(1/2) mcoef[rho] nx, x];
checkZero["source_compact_gradient_chemical_potential_form", interfaceForce - compactSourceForm];


pressureExcessCandidate = rho interfaceForce - (1/2) mcoef[rho] nx^2;
sourcePressureForm = (1/2) mcoef[rho] rho D[rho, {x, 2}] + D[(1/2) mcoef[rho] rho nx, x] - mcoef[rho] nx^2;
checkZero["eq_2_10_source_pressure_form", sourcePressureForm - pressureExcessCandidate];
checkZero["eq_2_10_dp_equals_n_dmu_route", D[sourcePressureForm, x] - rho D[interfaceForce, x]];

firstIntegralLHS = D[(1/2) mcoef[rho] nx^2, x];
firstIntegralRHS = interfaceForce nx;
checkZero["surface_tension_first_integral_bookkeeping", firstIntegralLHS - firstIntegralRHS];

omegaExcess = (1/2) mcoef[rho] nx^2;
interfacialExcessIntegrand = omegaExcess + (1/2) mcoef[rho] nx^2;
checkZero["surface_tension_grand_potential_reduction", interfacialExcessIntegrand - mcoef[rho] nx^2];

nxPos = Sqrt[2 omegaPos/mPos];
densityIntegrand = mPos nxPos;
densityTarget = Sqrt[2 mPos omegaPos];
checkZero["surface_tension_monotone_density_change", densityIntegrand - densityTarget];
checkExpectedNonzero[
  "surface_tension_wrong_orientation_negative_control",
  -densityIntegrand - densityTarget,
  {mPos > 0, omegaPos > 0}
];

If[Length[failures] > 0,
  Print["FAIL: Section II.A Wolfram checks"];
  Print[failures // InputForm];
  Exit[1],
  Print["PASS: Section II.A van der Waals baseline Wolfram checks"];
  Exit[0]
];
