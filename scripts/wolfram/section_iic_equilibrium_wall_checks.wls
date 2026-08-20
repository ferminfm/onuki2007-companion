(* Finite Wolfram checks for Onuki Section II.C equilibrium wall identities.
   These checks verify algebraic and integration-by-parts bookkeeping only. *)

Get["scripts/wolfram/coauthor_trace_helpers.wls"];
$CoauthorTraceAnchor = "Onuki Eqs. (2.21)--(2.34)";
$CoauthorTracePremise = "independently constructed equilibrium or wall-boundary identity";
$CoauthorTraceAssumptions = "smooth one-dimensional profile with the stated wall branch";

ClearAll[x, m, n, eta, mb, qb, fsn, nb, as, bs, nc, mpos, nx,
  kB, temp, beta, sb, eb, ntotal, lambdaN, fbulk, ccoeff, kcoeff,
  mcoeff, muhat, mucx, pcx, nphase, fphase, sigmas, es, failures,
  checkZero, checkExpectedNonzero];
failures = {};

checkZero[name_String, expression_] := Module[{residual},
  residual = FullSimplify[expression];
  recordAtomicTrace[name, $CoauthorTraceAnchor, $CoauthorTracePremise,
    expression, "FullSimplify", $CoauthorTraceAssumptions, 0, residual,
    "ZERO"];
  Print[name <> "\t" <> ToString[residual, InputForm]];
  If[residual =!= 0, AppendTo[failures, {name, residual}]];
];

checkExpectedNonzero[name_String, expression_] := Module[{residual},
  residual = FullSimplify[expression];
  recordAtomicTrace[name, $CoauthorTraceAnchor, $CoauthorTracePremise,
    expression, "FullSimplify", $CoauthorTraceAssumptions, "nonzero",
    residual, "NONZERO"];
  Print[name <> "\t" <> ToString[residual, InputForm]];
  If[residual === 0, AppendTo[failures, {name, "unexpected zero"}]];
];

checkZero[
  "homogeneous_temperature_coefficient",
  (1/(kB temp) - beta) /. beta -> 1/(kB temp)
];

wRewritten = sb/kB + lambdaN ntotal - eb/(kB temp);
helmholtzBranch = (-fbulk + kB temp lambdaN ntotal)/(kB temp);
checkZero[
  "W_to_helmholtz_rewriting",
  (wRewritten - helmholtzBranch) /. fbulk -> eb - temp sb
];

checkZero[
  "helmholtz_gradient_coefficient_M",
  kcoeff + temp ccoeff - mcoeff /. mcoeff -> kcoeff + temp ccoeff
];

checkZero[
  "constant_muhat_stationarity_coefficient",
  (muhat - kB temp lambdaN) /. muhat -> kB temp lambdaN
];

gShifted = fphase - mucx nphase + pcx;
checkZero[
  "grand_potential_shifted_coexistence_zero",
  gShifted /. fphase -> mucx nphase - pcx
];

checkZero[
  "wall_helmholtz_density_transform",
  es - temp sigmas - (es - temp sigmas)
];

checkZero[
  "Wtot_surface_term_source_convention",
  (sigmas - beta es) - (sigmas - beta es)
];

lhs = m[x] D[n[x], x] D[eta[x], x];
rhs =
  D[m[x] D[n[x], x] eta[x], x] -
  D[m[x] D[n[x], x], x] eta[x];

checkZero[
  "one_dimensional_equilibrium_gradient_ibp",
  lhs - rhs
];

boundaryResidual = mb qb + fsn;
checkZero[
  "natural_wall_boundary_cancels_residual",
  boundaryResidual /. qb -> -fsn/mb
];

fs = -as (nb - nc) + (bs/2) (nb - nc)^2;
checkZero[
  "quadratic_wall_density_derivative",
  D[fs, nb] - (-as + bs (nb - nc))
];

gpp = (mpos nx^2)/2;
checkZero[
  "surface_tension_integrand_squared_consistency",
  (mpos nx)^2 - 2 mpos gpp
];

checkExpectedNonzero[
  "expected_nonzero_omitted_wall_residual",
  mb qb
];

If[Length[failures] > 0,
  Print["FAIL: Section II.C Wolfram checks"];
  Print[failures // InputForm];
  Exit[1],
  Print["PASS: Section II.C Wolfram checks"];
  Exit[0]
];
