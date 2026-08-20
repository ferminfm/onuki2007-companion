(* Independent finite Wolfram checks for the Section III reading guide.
   These rows reconstruct scalar estimates only. They do not reproduce the
   source simulations, decide Appendix-B implementation, or validate fields. *)

ClearAll["Global`*"];

Get["scripts/wolfram/coauthor_trace_helpers.wls"];
$CoauthorTraceAnchor = "Onuki Section III Eqs. (3.3)--(3.20)";
$CoauthorTracePremise = "independently constructed finite reading-guide identity";
$CoauthorTraceAssumptions = "positive source scales; no numerical-field or implementation assumption";

$Assumptions = And @@ Thread[
  {nu0, mass, eps, ell, t0, sound, as, sigma, b, v0, n, length,
   gammaS, tau, q, kb, temp, dim, ts, deltaP, deltaTb, asl, asg,
   deltaTemp, vc, heatFlux, ng, deltaS, lambdaL, tempPrime, nu,
   lambdaEff, qIntegral, deltaWallTemp, bottomFlux, lambdaWall, gradTWall,
   q0, nc, grav, tc, pc, gstar} > 0
];

failures = {};
rows = {{"check_id", "status", "residual", "note"}};

addCheck[id_String, expression_, status_String, note_String] := Module[{residual},
  residual = FullSimplify[expression];
  recordAtomicTrace[id, $CoauthorTraceAnchor, $CoauthorTracePremise,
    expression, "FullSimplify", $CoauthorTraceAssumptions,
    If[status === "PASS_ZERO", 0, "nonzero"], residual,
    If[status === "PASS_ZERO", "ZERO", "NONZERO"]];
  AppendTo[rows, {id, status, ToString[residual, InputForm], note}];
  Print[id <> "\t" <> status <> "\t" <> ToString[residual, InputForm] <> "\t" <> note];
  If[status === "PASS_ZERO" && residual =!= 0, AppendTo[failures, {id, residual}]];
  If[status === "PASS_EXPECTED_NONZERO" && residual === 0,
    AppendTo[failures, {id, "unexpected zero"}]
  ];
];

addCheck[
  "III-01-sigma-forms",
  (nu0^2 mass/(eps ell^2) - mass ell^2/(eps t0^2)) /. t0 -> ell^2/nu0,
  "PASS_ZERO", "Eq. (3.6) after t0=ell^2/nu0"
];
addCheck[
  "III-02-sound-scale",
  t0 sound/ell - as/Sqrt[sigma] /. sound -> as ell/(t0 Sqrt[sigma]),
  "PASS_ZERO", "Eq. (3.8) sound scale"
];
addCheck[
  "III-03-transport-density-ratio",
  (Rationalize[1.70]/Rationalize[0.27]) - 170/27,
  "PASS_ZERO", "density-proportional transport ratio"
];
addCheck[
  "III-04-eq39-denominator",
  Sqrt[b/mass] Sqrt[mass/eps]/(1-v0 n) - Sqrt[b/eps]/(1-v0 n),
  "PASS_ZERO", "Eq. (3.9) retains the Eq. (2.5) denominator"
];
addCheck[
  "III-05-acoustic-traversal",
  length/(as ell/(t0 Sqrt[sigma])) - (length/ell) t0 Sqrt[sigma]/as,
  "PASS_ZERO", "acoustic traversal scale"
];
addCheck[
  "III-06-sound-damping",
  (2 nu0 + (2 nu0/gammaS) (gammaS-1))/(2 nu0) - (2-1/gammaS),
  "PASS_ZERO", "source attenuation convention"
];
addCheck[
  "III-07-capillary-wave",
  (t0 Sqrt[eps ell tau^(3/2) (q/ell)^3/mass] - tau^(3/4) q^(3/2)/Sqrt[sigma]) /.
    sigma -> mass ell^2/(eps t0^2),
  "PASS_ZERO", "Eq. (3.11) capillary-wave scaling"
];

pVdw = n kb temp/(1-v0 n) - eps v0 n^2;
tsExpr = 2 eps v0 n (1-v0 n)^2/kb;
addCheck[
  "III-08-inverse-compressibility",
  n D[pVdw, n] - kb n (temp-tsExpr)/(1-v0 n)^2,
  "PASS_ZERO", "Eq. (3.12) from the pressure derivative"
];
tnS = 2 temp/(dim n (1-v0 n));
pnS = kb temp/(1-v0 n)^2 (1+2/dim-ts/temp);
addCheck[
  "III-09-adiabatic-coefficient-d2",
  (tnS/pnS /. dim -> 2) - (1/n-v0)/(kb (2-ts/temp)),
  "PASS_ZERO", "Eq. (3.14) in d=2"
];
addCheck[
  "III-10-pressure-estimate",
  deltaP-deltaTb/asl /. deltaP -> deltaTb/asl,
  "PASS_ZERO", "Eq. (3.13) scalar estimate"
];
addCheck[
  "III-11-phase-temperature-contrast",
  deltaTemp-(asg-asl) deltaP /. deltaTemp -> (asg-asl) deltaP,
  "PASS_ZERO", "Eq. (3.15) subtraction"
];
addCheck[
  "III-12-latent-heat-velocity",
  vc-heatFlux/(ng temp deltaS) /. vc -> heatFlux/(ng temp deltaS),
  "PASS_ZERO", "Eq. (3.16) velocity definition"
];
addCheck[
  "III-13-latent-gradient-branch",
  vc+lambdaL tempPrime/(ng temp deltaS) /. vc -> -lambdaL tempPrime/(ng temp deltaS),
  "PASS_ZERO", "far-field Fourier branch"
];
addCheck[
  "III-14A-effective-conductivity-definition",
  lambdaEff-qIntegral/deltaWallTemp /. lambdaEff -> qIntegral/deltaWallTemp,
  "PASS_ZERO", "Eq. (3.17) integrated bottom-wall definition"
];
addCheck[
  "III-14B-bottom-heat-flux-definition",
  bottomFlux+lambdaWall gradTWall /. bottomFlux -> -lambdaWall gradTWall,
  "PASS_ZERO", "Eq. (3.18) conductive wall-flux diagnostic"
];
addCheck[
  "III-14-nusselt-definition",
  nu-lambdaEff/lambdaL /. nu -> lambdaEff/lambdaL,
  "PASS_ZERO", "Eq. (3.19) definition"
];
addCheck[
  "III-15-no-convection-nusselt",
  nu-n/(Rationalize[1.7] nc) /. nu -> n/(Rationalize[1.7] nc),
  "PASS_ZERO", "one-phase no-convection estimate"
];
addCheck[
  "III-16-adiabatic-gradient-order",
  mass n grav tc/pc - gstar tc/ell /.
    {n -> 1/v0, pc -> eps/v0, gstar -> mass grav ell/eps},
  "PASS_ZERO", "Eq. (3.20) order scale"
];
addCheck[
  "III-17-wetting-heat-flux-normalization",
  q0-eps ell/(v0 t0) /. q0 -> eps ell/(v0 t0),
  "PASS_ZERO", "Section III.G plot-reading heat-flux scale"
];
addCheck[
  "III-NEG-01-eq39-missing-denominator",
  Sqrt[b/eps] - Sqrt[b/eps]/(1-v0 n),
  "PASS_EXPECTED_NONZERO", "dropping the Eq. (2.5) denominator is fragile"
];

AppendTo[rows, {"III-STATUS-no-numerical-reproduction", "NOT_REPRODUCED", "not_applicable",
  "finite reading-guide estimates only"}];
AppendTo[rows, {"III-STATUS-unpublished-code", "UNRESOLVED_SOURCE_DEPENDENT", "not_applicable",
  "the unpublished simulation-code branch is not inferred"}];

If[!DirectoryQ["generated/wolfram"],
  CreateDirectory["generated/wolfram", CreateIntermediateDirectories -> True]
];
Export["generated/wolfram/section_iii_simulation_estimates_summary.tsv", rows, "TSV"];

If[Length[failures] > 0,
  Print["FAIL: Section III simulation-estimate checks"];
  Print[failures // InputForm];
  Exit[1],
  Print["PASS: Section III simulation-estimate checks"];
  Exit[0]
];
