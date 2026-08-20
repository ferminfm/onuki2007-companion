# Theorem Index and Hand Proofs

All declarations below are in module `Korteweg1901.TensorKernels`, file
`formal/korteweg1901_mathlib/Korteweg1901/TensorKernels.lean`. The companion
anchors are Appendices C and E. The variables model finitely many real
components; they are not functions on a continuum domain.

## `dyadic_gradient_stress_symmetric`

```lean
theorem dyadic_gradient_stress_symmetric {n : Nat} (g : Fin n -> Real)
    (i j : Fin n) : Dyadic g i j = Dyadic g j i
```

`Dyadic g i j` is `g i * g j`. **Hand proof:** commute the two real factors:
`g i * g j = g j * g i`. The theorem checks the component symmetry of a dyadic
product used in Appendix E. It does not prove symmetry of a differentiable
stress field.

## `finite_stress_contraction_two_dim`

```lean
theorem finite_stress_contraction_two_dim
    (gx gy uxx uxy uyx uyy : Real) :
    (sum over i,j : Fin 2 of Dyadic (vectorTwo gx gy) i j *
      matrixTwo uxx uxy uyx uyy i j) =
      gx*gx*uxx + gx*gy*uxy + gy*gx*uyx + gy*gy*uyy
```

**Hand proof:** expand the four pairs `(0,0)`, `(0,1)`, `(1,0)`, and `(1,1)`.
Insert `Dyadic(g)_ij=g_i g_j` and the four entries of `matrixTwo`; the four
summands are the right side. This is the finite component expansion behind the
stress-contraction display in Appendix C. It does not establish an integral
stress-power identity.

## `capillary_divergence_collection_kernel`

```lean
theorem capillary_divergence_collection_kernel
    (alpha beta gamma deltaK q lap alphaI gammaI betaJgJ deltaJhIJ
      hIJgJ rhoI lapI : Real) :
    q*alphaI - lap*gammaI + betaJgJ*rhoI - deltaJhIJ +
      2*alpha*hIJgJ + beta*hIJgJ + beta*rhoI*lap - gamma*lapI - deltaK*lapI =
    q*alphaI - lap*gammaI + betaJgJ*rhoI - deltaJhIJ +
      (2*alpha+beta)*hIJgJ + beta*rhoI*lap - (gamma+deltaK)*lapI
```

**Hand proof:** distribute the two parentheses on the right. The coefficient of
`hIJgJ` is `2 alpha + beta` and the coefficient of `lapI` is
`-(gamma + deltaK)`, reproducing the left side. Appendix E supplies the
product-rule calculation that leads to these placeholder components. Lean
checks only their final polynomial collection; it neither differentiates fields
nor justifies a mixed-derivative interchange.

## `density_gradient_coefficient_map`

```lean
theorem density_gradient_coefficient_map
    (coefficient massScale gradI gradJ : Real) :
    coefficient*(massScale*gradI)*(massScale*gradJ) =
      (coefficient*massScale^2)*gradI*gradJ
```

**Hand proof:** reassociate the product and collect the two equal mass-scale
factors: `massScale * massScale = massScale^2`. This is the finite coefficient
calculation used when a constant linear density normalization is introduced in
Appendix C. It does not prove a density-field change of variables.

## `density_hessian_coefficient_map`

```lean
theorem density_hessian_coefficient_map
    (coefficient massScale hessianIJ : Real) :
    coefficient*(massScale*hessianIJ) = (coefficient*massScale)*hessianIJ
```

**Hand proof:** use associativity of multiplication. This checks one scalar
coefficient rearrangement for a Hessian component. It assumes that such a
component is already defined and does not provide weak-derivative regularity.

## `pressure_to_cauchy_force_bridge`

```lean
theorem pressure_to_cauchy_force_bridge
    (body divP divSigma : Real) (hdiv : divSigma = -divP) :
    body - divP = body + divSigma
```

**Hand proof:** substitute `divSigma=-divP` into the right side, giving
`body + (-divP)`, then use `a+(-b)=a-b`. The sign convention is stated in
Appendices C and E. The theorem does not derive the divergence hypothesis from
a stress constitutive law or a momentum balance.

## `divergence_match_not_literal_tensor_match`

```lean
theorem divergence_match_not_literal_tensor_match
    (comparison : TensorForceComparison)
    (_hdiv : comparison.divergenceEquality)
    (hnotLiteral : not comparison.literalTensorEquality) :
    not (LiteralAndDivergenceMatch comparison)
```

**Hand proof:** assume `LiteralAndDivergenceMatch`. Its first component asserts
literal tensor equality, contradicting `hnotLiteral`. This is a logical
guardrail for Appendix E: equal divergence data alone cannot be reported as
literal tensor equality. It does not construct a stress gauge or settle
boundary tractions.

## `dyadic_quadratic_nonnegative`

```lean
theorem dyadic_quadratic_nonnegative
    (coefficient gx gy : Real) (hcoefficient : 0 <= coefficient) :
    0 <= coefficient*(gx^2 + gy^2)
```

**Hand proof:** real squares are nonnegative, so `gx^2 + gy^2 >= 0`. Its
product with the assumed nonnegative coefficient is nonnegative. This finite
order fact does not prove entropy production, thermodynamic admissibility, or
positivity of a continuum dissipation functional.

## Audit Commands

Run `bash scripts/verify_formal_project.sh` to rebuild the project, scan its
source for `sorry`, `admit`, and custom `axiom` declarations, and print the
theorem inventory. `research_notes/korteweg_lean_theorem_to_paper_map.csv` is
the machine-readable companion map. Its scope limits are part of every
theorem's interpretation.
