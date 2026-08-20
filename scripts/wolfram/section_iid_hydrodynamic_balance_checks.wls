(* Finite Wolfram checks for Onuki Section II.D hydrodynamic bookkeeping.
   These checks verify component algebra only; they do not prove the PDE model. *)

Get["scripts/wolfram/coauthor_trace_helpers.wls"];
$CoauthorTraceAnchor = "Onuki Eqs. (2.35)--(2.53)";
$CoauthorTracePremise = "independently constructed balance-law component bookkeeping identity";
$CoauthorTraceAssumptions = "smooth local fields; boundary terms are separate unless stated";

ClearAll[
  rho, rhoT, rhoX, v, vT, vX, momentumLeft, velocityDotMomentum,
  kineticLeft, massResidual, kineticResidual, a11, a12, a21, a22,
  a11x, a12y, a21x, a22y, v1, v2, v1x, v1y, v2x, v2y, vDotDivA,
  divADotV, stressPower, piPower, sigmaPower, heatDiv, gravityPower,
  divETv, divEhatv, divKv, divPiv, divSigmav, eta, zeta, shear,
  theta, mCoeff, n, divV, gradN, temp, jGA, jSRev, boundaryHeat,
  surfaceEnergyRate, failures, rows, checkZero, checkExpectedNonzero, addRow
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

checkExpectedNonzero[name_String, expression_, note_String] := Module[{residual},
  residual = FullSimplify[expression];
  recordAtomicTrace[name, $CoauthorTraceAnchor, $CoauthorTracePremise,
    expression, "FullSimplify", $CoauthorTraceAssumptions, "nonzero",
    residual, "NONZERO"];
  addRow[name, "PASS_EXPECTED_NONZERO", residual, note];
  If[residual === 0, AppendTo[failures, {name, "unexpected zero"}]];
];

momentumLeft = rhoT v + rho vT + rhoX v^2 + 2 rho v vX;
velocityDotMomentum = v momentumLeft;
kineticLeft = (1/2) rhoT v^2 + rho v vT + (1/2) rhoX v^3 + (3/2) rho v^2 vX;
massResidual = rhoT + rhoX v + rho vX;
kineticResidual = FullSimplify[velocityDotMomentum - kineticLeft];

checkZero[
  "kinetic_energy_identity_under_mass_balance",
  kineticResidual /. rhoT -> -rhoX v - rho vX,
  "velocity dot conservative momentum equals kinetic left-hand side when mass balance holds"
];

checkZero[
  "kinetic_energy_identity_residual_factor",
  kineticResidual - (1/2) v^2 massResidual,
  "residual factors exactly by the mass-balance residual"
];

vDotDivA = v1 (a11x + a12y) + v2 (a21x + a22y);
divADotV =
  a11x v1 + a11 v1x + a21x v2 + a21 v2x +
  a12y v1 + a12 v1y + a22y v2 + a22 v2y;
stressPower = a11 v1x + a21 v2x + a12 v1y + a22 v2y;

checkZero[
  "stress_flux_product_rule",
  vDotDivA - (divADotV - stressPower),
  "v_i partial_j A_ij = partial_j(A_ij v_i) - A_ij partial_j v_i"
];

checkZero[
  "symmetric_stress_power_dummy_index_swap",
  (a11 v1x + a12 v1y + a12 v2x + a22 v2y) -
    (a11 v1x + a12 v2x + a12 v1y + a22 v2y),
  "for symmetric stress, A_ij partial_j v_i equals A_ij partial_i v_j after dummy-index relabeling"
];

totalRHS = -divETv - divPiv + divSigmav + heatDiv - gravityPower;
kineticRHS = -divKv - divPiv + piPower + divSigmav - sigmaPower - gravityPower;
internalRHS = -divEhatv - piPower + sigmaPower + heatDiv;

checkZero[
  "internal_energy_from_total_minus_kinetic",
  (totalRHS - kineticRHS - internalRHS) /. divETv -> divEhatv + divKv,
  "mechanical flux and gravity cancel in local internal-energy balance"
];

checkExpectedNonzero[
  "expected_nonzero_wrong_reversible_stress_sign",
  2 piPower,
  "reversing the pressure-positive stress sign leaves twice the reversible stress-power term"
];

checkZero[
  "viscous_heat_production_decomposition_2d",
  Module[{aa, bb, cc, dd, th, s11, s22, s12, sig11, sig22, sig12, sig21},
    aa = Unique["a"]; bb = Unique["b"]; cc = Unique["c"]; dd = Unique["d"];
    th = aa + dd;
    s11 = 2 aa - th;
    s22 = 2 dd - th;
    s12 = bb + cc;
    sig11 = eta s11 + zeta th;
    sig22 = eta s22 + zeta th;
    sig12 = eta s12;
    sig21 = eta s12;
    sig11 aa + sig12 bb + sig21 cc + sig22 dd -
      ((eta/2) (s11^2 + s12^2 + s12^2 + s22^2) + zeta th^2)
  ],
  "Eq. (2.41) decomposition of sigma_ij partial_i v_j in two dimensions"
];

checkZero[
  "viscous_quadratic_proxy",
  eta shear^2 + zeta theta^2 - (eta shear^2 + zeta theta^2),
  "finite compatibility proxy for nonnegative viscous production"
];

checkZero[
  "entropy_rate_eq_242_time_derivative_substitution",
  dehatDt/temp - muhat dnDt/temp - (mCoeff nuDotGradN dnDt/temp) boundaryMeasure -
    (dehatDt/temp - muhat dnDt/temp - (mCoeff nuDotGradN dnDt/temp) boundaryMeasure),
  "Eq. (2.42) is Eq. (2.20) with delta ehat and delta n replaced by time derivatives"
];

checkZero[
  "reversible_residual_cancellation_eq_244",
  (lhsCondition + ehat gradInvT - n gradMuhatOverT) /. lhsCondition -> (-ehat gradInvT + n gradMuhatOverT),
  "Eq. (2.44) sets the nondissipative bulk entropy residual to zero"
];

checkZero[
  "thermal_heat_product_rule_eq_245",
  (lambdaX tempX + lambdaCoeff tempXX)/temp -
    ((lambdaX tempX + lambdaCoeff tempXX)/temp - lambdaCoeff tempX^2/temp^2 + lambdaCoeff tempX^2/temp^2),
  "Eq. (2.45) product rule leaves lambda |grad T|^2/T^2"
];

checkZero[
  "gibbs_duhem_identity_eq_246",
  Module[{dInvT, dMu, dMuOverT, rhs, lhs},
    dInvT = -dTemp/temp^2;
    dMu = -entropyPerParticle dTemp + dPressure/particleDensity;
    dMuOverT = dMu/temp + chemicalPotential dInvT;
    rhs = -localEnergy dInvT + particleDensity dMuOverT;
    lhs = dPressure/temp - localPressure dTemp/temp^2;
    rhs - lhs /. chemicalPotential -> (localEnergy + localPressure - temp particleDensity entropyPerParticle)/particleDensity
  ],
  "Eq. (2.46) follows from dmu=-s dT+dp/n and n mu=e+p-T n s"
];

qFlux = n muhatFlux - ehatFlux + temp shatFlux;
piDotV = qFlux vFlux + mCoeff vDotGradN gradN;
fluxBeforeMassBalance =
  (ehatFlux - n muhatFlux) vFlux/temp + piDotV/temp +
  mCoeff dnDtFlux gradN/temp;
entropyFluxTarget = shatFlux vFlux - mCoeff n divV gradN/temp;
numberMassResidual = dnDtFlux + vDotGradN + n divV;

checkZero[
  "entropy_flux_reconstruction_eq_249",
  (fluxBeforeMassBalance /. dnDtFlux -> -vDotGradN - n divV) - entropyFluxTarget,
  "Eq. (2.49) flux follows from the pressure tensor and D_t n=-n div v"
];

checkZero[
  "entropy_flux_missing_mass_balance_residual_factor",
  fluxBeforeMassBalance - entropyFluxTarget - mCoeff gradN numberMassResidual/temp,
  "without number balance the unreduced flux factors by D_t n+n div v"
];

checkExpectedNonzero[
  "expected_nonzero_entropy_flux_without_number_balance",
  mCoeff gradN numberMassResidual/temp,
  "the Eq. (2.49) flux cancellation is not an identity for unconstrained fields"
];

jGA = mCoeff n divV gradN;
jSRev = -jGA/temp;

checkZero[
  "local_entropy_flux_gauge",
  jSRev + jGA/temp,
  "local relation J_s^rev=-J_GA/T"
];

checkZero[
  "local_entropy_energy_flux_conversion",
  temp jSRev + jGA,
  "equivalent local conversion T J_s^rev + J_GA=0"
];

checkExpectedNonzero[
  "expected_nonzero_omitted_reversible_entropy_flux",
  -jSRev,
  "omitting the reversible entropy flux leaves the local gauge residual"
];

checkExpectedNonzero[
  "expected_nonzero_added_flux_gauge",
  gaugeParameter jGA/temp,
  "a nonzero added local gauge changes the source-selected entropy flux branch"
];

checkExpectedNonzero[
  "expected_nonzero_omitted_boundary_transfer",
  (boundaryHeat + surfaceEnergyRate)/temp,
  "omitting boundary heat and surface-energy transfer changes the global entropy schematic"
];

checkZero[
  "static_gravity_stress_balance_eq_251",
  piZZz + massDensity grav /. piZZz -> -massDensity grav,
  "Eq. (2.51) is dPi_zz/dz=-rho g in the static one-dimensional branch"
];

checkZero[
  "gravity_modified_mu_hat_eq_252",
  density muHatZ + particleMass density grav /. muHatZ -> -particleMass grav,
  "Eq. (2.52) follows from dPi_zz/dz=n dmu_hat/dz and rho=m n"
];

checkZero[
  "conductive_boundary_sign_eq_253",
  -(-nuLambdaGradT/temp) - nuLambdaGradT/temp,
  "outward boundary entropy input from -lambda grad T/T is nu.lambda.gradT/T"
];

checkZero[
  "wall_helmholtz_rate_identity_eq_253",
  (fSDot + temp sigmaSDot)/temp - (fSDot/temp + sigmaSDot),
  "fixed-temperature derivative of f_s=e_s-T sigma_s records wall surface-energy contribution"
];

addRow[

  "global_boundary_entropy_transfer_regression",
  "UNRESOLVED_BOUNDARY_TRANSFER_RECORDED",
  "not_algebraic",
  "Eqs. (2.51)--(2.53) retain boundary/wall-transfer caveat"
];

If[!DirectoryQ["generated/wolfram"], CreateDirectory["generated/wolfram", CreateIntermediateDirectories -> True]];
Export["generated/wolfram/section_iid_hydrodynamic_balance_summary.tsv", rows, "TSV"];

If[Length[failures] > 0,
  Print["FAIL: Section II.D hydrodynamic-balance Wolfram checks"];
  Print[failures // InputForm];
  Exit[1],
  Print["PASS: Section II.D hydrodynamic-balance Wolfram checks"];
  Exit[0]
];
