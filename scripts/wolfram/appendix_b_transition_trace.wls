(* Transition-level Wolfram trace for Onuki Appendix B, Eqs. (B1)--(B6).
   Each row records source object, substitution, intermediate expression,
   expected scaled expression, and residual. The trace checks finite scaling
   only; it does not infer the unpublished implementation or reproduce runs. *)

ClearAll["Global`*"];

failures = {};
rows = {{
  "transition_id", "source_object", "substitution", "intermediate",
  "expected_output", "residual", "status", "note"
}};

addTrace[id_String, source_String, substitution_String, intermediate_, expected_,
  status_String, note_String] := Module[{residual},
  residual = FullSimplify[intermediate - expected];
  AppendTo[rows, {
    id, source, substitution, ToString[intermediate, InputForm],
    ToString[expected, InputForm], ToString[residual, InputForm], status, note
  }];
  Print[id <> "\t" <> status <> "\t" <> ToString[residual, InputForm] <> "\t" <> note];
  If[status === "PASS_ZERO" && residual =!= 0,
    AppendTo[failures, {id, residual}]
  ];
  If[status === "PASS_EXPECTED_NONZERO" && residual === 0,
    AppendTo[failures, {id, "unexpected zero"}]
  ];
];

(* B1: field and operator substitutions. *)
addTrace[
  "B1-01-time-operator", "partial_t phi", "t=t0 t*",
  dtPhi/t0, dtPhi/t0, "PASS_ZERO",
  "time derivative carries t0^-1"
];
addTrace[
  "B1-02-space-operator", "partial_x phi", "x=ell x*",
  phiX/ell, phiX/ell, "PASS_ZERO",
  "spatial derivative carries ell^-1"
];
addTrace[
  "B1-03-density-gradient", "grad_x n", "n=phi/v0; x=ell x*",
  phiX/(v0 ell), phiX/(v0 ell), "PASS_ZERO",
  "density and coordinate scales both remain visible"
];

(* B2: continuity and momentum prefactors. *)
continuityDimensional = phiT/(v0 t0) + divPhiV/(v0 t0);
addTrace[
  "B2-01-continuity", "partial_t n+div_x(n v)",
  "n=phi/v0; v=(ell/t0)V; operators from B1",
  v0 t0 continuityDimensional, phiT + divPhiV, "PASS_ZERO",
  "common 1/(v0 t0) prefactor cancels"
];
sigmaDef = m ell^2/(eps t0^2);
addTrace[
  "B2-02-inertial-prefactor", "(ell v0/eps) partial_t(rho v)",
  "rho=m phi/v0; v=(ell/t0)V",
  m ell^2/(eps t0^2), sigmaDef, "PASS_ZERO",
  "time-inertial coefficient is sigma"
];
addTrace[
  "B2-03-convective-prefactor", "(ell v0/eps) div_x(rho v v)",
  "rho=m phi/v0; v=(ell/t0)V; div_x=ell^-1 div_*",
  m ell^2/(eps t0^2), sigmaDef, "PASS_ZERO",
  "convective coefficient is the same sigma"
];
gStar = m g ell/eps;
addTrace[
  "B2-04-gravity-prefactor", "(ell v0/eps) rho g",
  "rho=m phi/v0",
  m g ell phi/eps, gStar phi, "PASS_ZERO",
  "gravity force scales to g* phi"
];

(* B3: dimensional-source tensor terms. *)
mCoeff = 2 eps v0 ell^2 theta;
addTrace[
  "B3-01-gradient-square", "(v0/eps)(-M |grad_x n|^2/2)",
  "M=2 eps v0 ell^2 Theta; grad_x n=grad phi/(v0 ell)",
  (v0/eps) (-mCoeff gradPhiSq/(2 v0^2 ell^2)),
  -theta gradPhiSq, "PASS_ZERO",
  "diagonal gradient-square term"
];
addTrace[
  "B3-02-diagonal-laplacian", "(v0/eps)(-M n Delta_x n)",
  "n=phi/v0; Delta_x n=Delta phi/(v0 ell^2)",
  (v0/eps) (-mCoeff (phi/v0) lapPhi/(v0 ell^2)),
  -2 theta phi lapPhi, "PASS_ZERO",
  "dimensional-source branch retains phi"
];
addTrace[
  "B3-03-gradient-dyad", "(v0/eps) M partial_i n partial_j n",
  "partial_x n=partial phi/(v0 ell)",
  (v0/eps) mCoeff phiI phiJ/(v0^2 ell^2),
  2 theta phiI phiJ, "PASS_ZERO",
  "off-diagonal dyad coefficient"
];
sourceDiag = p0 - theta gradPhiSq - 2 theta phi lapPhi;
printedDiag = p0 - theta gradPhiSq - 2 theta lapPhi;
addTrace[
  "B3-04-printed-source-residual", "M_print-M_dim",
  "preserve both source branches",
  printedDiag, sourceDiag, "PASS_EXPECTED_NONZERO",
  "residual is 2 Theta (phi-1) Delta phi"
];

(* B4: scaled local energy density. *)
energyIntermediate = phi theta - phi^2 + sigma phi vSq/2;
addTrace[
  "B4-01-energy-density", "(v0/eps) e_T",
  "d=2; K=0; rho=m phi/v0; v=(ell/t0)V",
  energyIntermediate, phi theta - phi^2 + sigma phi vSq/2,
  "PASS_ZERO", "local energy-density scaling"
];

(* B5: flux and source terms. *)
addTrace[
  "B5-01-conduction", "(v0 t0/eps) div_x(lambda grad_x T)",
  "lambda=kB nu0 phi/v0; T=eps Theta/kB; t0=ell^2/nu0",
  (t0 nu0/ell^2 /. t0 -> ell^2/nu0) divPhiGradTheta,
  divPhiGradTheta, "PASS_ZERO",
  "heat-diffusion coefficient reduces to one"
];
addTrace[
  "B5-02-stress-flux", "scaled div_x(Pi.v)",
  "Pi=(eps/v0) Mscript; v=(ell/t0)V",
  (t0/ell) (ell/t0) stressFluxScaled,
  stressFluxScaled, "PASS_ZERO",
  "all dimensional velocity factors cancel before stars are suppressed"
];
addTrace[
  "B5-03-gravity-power", "-(v0 t0/eps) rho g v_z",
  "rho=m phi/v0; v_z=(ell/t0)V_z",
  -(v0 t0/eps) (m phi/v0) g (ell/t0) vz,
  -gStar phi vz, "PASS_ZERO",
  "source gravity-work sign retained"
];

(* B6: scale the two sides independently before equating them. *)
addTrace[
  "B6-01-left-side", "v0 [2 sqrt(2) ell nu.grad_x n]",
  "nu.grad_x n=gradNormalPhi/(v0 ell)",
  v0 2 Sqrt[2] ell (gradNormalPhi/(v0 ell)),
  2 Sqrt[2] gradNormalPhi, "PASS_ZERO",
  "normal derivative is expressed in scaled coordinates"
];
addTrace[
  "B6-02-right-side", "v0 [n-5 n_c/2]",
  "n=phi/v0; n_c=1/(3 v0)",
  v0 (phi/v0 - 5/(2 3 v0)),
  phi - 5/6, "PASS_ZERO",
  "source wetting parameter and critical density give 5/6"
];

(* Required fragile-term negative controls. *)
addTrace[
  "NEG-01-wrong-coordinate-derivative", "grad_x n",
  "incorrectly omit ell^-1",
  v0 ell (phiX/v0), v0 ell (phiX/(v0 ell)),
  "PASS_EXPECTED_NONZERO", "uncancelled ell marks mixed coordinates"
];
addTrace[
  "NEG-02-missing-kinetic-density", "B4 kinetic density",
  "incorrectly drop phi",
  sigma vSq/2, sigma phi vSq/2,
  "PASS_EXPECTED_NONZERO", "kinetic energy is a density and retains phi"
];
addTrace[
  "NEG-03-wrong-gravity-sign", "B5 gravity power",
  "incorrectly reverse source sign",
  gStar phi vz, -gStar phi vz,
  "PASS_EXPECTED_NONZERO", "wrong sign leaves twice the source term"
];
addTrace[
  "NEG-04-mixed-velocity", "B5 stress flux",
  "retain dimensional v instead of V=(t0/ell)v",
  (t0/ell) stressFluxDimensional,
  stressFluxScaled, "PASS_EXPECTED_NONZERO",
  "independent dimensional and scaled velocity symbols cannot be mixed"
];

AppendTo[rows, {
  "STATUS-01-unpublished-code", "simulation implementation", "not available",
  "not_algebraic", "not_inferred", "not_applicable",
  "UNRESOLVED_SOURCE_DEPENDENT",
  "printed and dimensional-source branches do not identify unpublished code"
}];

If[!DirectoryQ["generated/wolfram"],
  CreateDirectory["generated/wolfram", CreateIntermediateDirectories -> True]
];
Export["generated/wolfram/appendix_b_transition_trace.tsv", rows, "TSV"];

If[Length[failures] > 0,
  Print["FAIL: Appendix B transition trace"];
  Print[failures // InputForm];
  Exit[1],
  Print["PASS: Appendix B transition trace"];
  Exit[0]
];
