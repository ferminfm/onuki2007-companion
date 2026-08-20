(* Finite Wolfram checks for Onuki Appendix A reversible-stress bookkeeping.
   These checks verify component algebra only; they do not prove the PDE model. *)

Get["scripts/wolfram/coauthor_trace_helpers.wls"];
$CoauthorTraceAnchor = "Onuki Eqs. (A1)--(A4) and Eq. (2.47)";
$CoauthorTracePremise = "independently constructed finite component or virtual-displacement identity";
$CoauthorTraceAssumptions = "smooth finite component fields and the displayed sign convention";

ClearAll[x, y, x1, n, ux, uy, m, eta, M, nx, ny, pdiag, uxx, uxy, uyx, uyy,
  eps, a11, a12, a21, a22, n0, divu, dnx, dny, uyxSym, uxySym,
  temp, shat, ehat, nhat, muhat, pixx, pixy, piyx, piyy, pLocal, p1,
  failures, checkZero, checkExpectedNonzero];
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

deformation = {{1 + eps a11, eps a12}, {eps a21, 1 + eps a22}};
detSeries = Normal[Series[Det[deformation], {eps, 0, 1}]];
checkZero[
  "determinant_first_order_trace",
  detSeries - (1 + eps (a11 + a22))
];

densitySeries = Normal[Series[n0/(1 + eps divu), {eps, 0, 1}]];
checkZero[
  "material_density_variation_A1",
  densitySeries - (n0 - eps n0 divu)
];

gradXPrime = nx + eps (dnx - uxx nx - uyxSym ny);
gradYPrime = ny + eps (dny - uxySym nx - uyy ny);
gradSquarePrime = (gradXPrime^2 + gradYPrime^2)/2;
gradSquareBase = (nx^2 + ny^2)/2;
gradSquareDelta = Coefficient[Expand[gradSquarePrime - gradSquareBase], eps, 1];
gradSquareTarget = nx dnx + ny dny - (nx^2 uxx + nx ny uyxSym + ny nx uxySym + ny^2 uyy);
checkZero[
  "gradient_square_variation_A3",
  gradSquareDelta - gradSquareTarget
];

deltaNxMaterial = -nx thetaU - n0 thetaX;
deltaNyMaterial = -ny thetaU - n0 thetaY;
materialGradientChange =
  nx deltaNxMaterial + ny deltaNyMaterial -
  (nx^2 uxx + nx ny uyxSym + ny nx uxySym + ny^2 uyy);
materialGradientTarget =
  -(nx^2 + ny^2) thetaU - n0 (nx thetaX + ny thetaY) -
  (nx^2 uxx + nx ny uyxSym + ny nx uxySym + ny^2 uyy);
checkZero[
  "material_gradient_variation_A3_substitution",
  materialGradientChange - materialGradientTarget
];

coeffXX = temp shat - ehat + nhat muhat - pixx + M nx^2;
coeffXY = -pixy + M nx ny;
checkZero[
  "entropy_variation_A4_coefficients",
  coeffXX - ((temp shat - ehat + nhat muhat) - pixx + M nx^2)
];

stressDiag = temp shat - ehat + nhat muhat;
checkZero[
  "stress_identification_residual_A4",
  coeffXX /. pixx -> stressDiag + M nx^2
];
checkZero[
  "offdiagonal_stress_identification_residual_A4",
  coeffXY /. pixy -> M nx ny
];
checkZero[
  "p1_bridge_to_pressure_tensor",
  ((pLocal + p1) /. p1 -> nhat muhat - ehat + temp shat - pLocal) - stressDiag
];

divNu = D[n[x, y] ux[x, y], x] + D[n[x, y] uy[x, y], y];
productRule =
  ux[x, y] D[n[x, y], x] +
  uy[x, y] D[n[x, y], y] +
  n[x, y] (D[ux[x, y], x] + D[uy[x, y], y]);

checkZero[
  "density_variation_product_rule",
  divNu - productRule
];

checkZero[
  "eulerian_density_variation",
  (-divNu) - (-productRule)
];

lhs = m[x1] D[n[x1], x1] D[eta[x1], x1];
rhs =
  D[m[x1] D[n[x1], x1] eta[x1], x1] -
  D[m[x1] D[n[x1], x1], x1] eta[x1];

checkZero[
  "one_dimensional_gradient_ibp",
  lhs - rhs
];

retainedBoundaryDensity = m[x1] n[x1] D[n[x1], x1] thetaFunction[x1];
materialMiddleTerm =
  m[x1] n[x1] D[n[x1], x1] D[thetaFunction[x1], x1];
materialBulkTerm =
  -thetaFunction[x1] D[m[x1] n[x1] D[n[x1], x1], x1];
checkZero[
  "material_gradient_ibp_with_boundary_A3",
  materialMiddleTerm - (D[retainedBoundaryDensity, x1] + materialBulkTerm)
];

omittedBoundaryResidual =
  D[(1 + x1) (1 + x1^2) D[1 + x1^2, x1] x1^2, x1];
checkExpectedNonzero[
  "expected_nonzero_omitted_material_gradient_boundary",
  omittedBoundaryResidual
];

piXX = pdiag + M nx^2;
piXY = M nx ny;
piYX = M ny nx;
piYY = pdiag + M ny^2;

checkZero[
  "off_diagonal_stress_symmetry",
  piXY - piYX
];

stressPower = piXX uxx + piXY uxy + piYX uyx + piYY uyy;
target =
  pdiag (uxx + uyy) +
  M (nx^2 uxx + nx ny uxy + ny nx uyx + ny^2 uyy);

checkZero[
  "component_stress_power_contraction",
  stressPower - target
];

checkExpectedNonzero[
  "expected_nonzero_omitted_offdiagonal_residual",
  stressPower - (piXX uxx + piYY uyy)
];

If[Length[failures] > 0,
  Print["FAIL: Appendix A reversible-stress Wolfram checks"];
  Print[failures // InputForm];
  Exit[1],
  Print["PASS: Appendix A reversible-stress Wolfram checks"];
  Exit[0]
];
