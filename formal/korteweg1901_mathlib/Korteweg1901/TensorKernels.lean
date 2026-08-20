import Mathlib

namespace Korteweg1901

/-!
Finite algebraic and logical kernels used by the Korteweg 1901 reconstruction.

These theorems do not differentiate continuum fields, prove a balance law,
select constitutive coefficients, or establish an Onuki equivalence.
-/

/-- A finite dyadic product used as a component model of `g tensor g`. -/
def Dyadic {n : Nat} (g : Fin n → Real) : Fin n → Fin n → Real :=
  fun i j => g i * g j

theorem dyadic_gradient_stress_symmetric {n : Nat} (g : Fin n → Real)
    (i j : Fin n) :
    Dyadic g i j = Dyadic g j i := by
  simp [Dyadic, mul_comm]

/-- A two-component vector for explicit finite sums. -/
def vectorTwo (x y : Real) : Fin 2 → Real
  | 0 => x
  | 1 => y

/-- A two-by-two component array. -/
def matrixTwo (a11 a12 a21 a22 : Real) : Fin 2 → Fin 2 → Real
  | 0, 0 => a11
  | 0, 1 => a12
  | 1, 0 => a21
  | 1, 1 => a22

theorem finite_stress_contraction_two_dim
    (gx gy uxx uxy uyx uyy : Real) :
    (∑ i : Fin 2, ∑ j : Fin 2,
      Dyadic (vectorTwo gx gy) i j * matrixTwo uxx uxy uyx uyy i j) =
      gx * gx * uxx + gx * gy * uxy + gy * gx * uyx + gy * gy * uyy := by
  simp [Dyadic, vectorTwo, matrixTwo, Fin.sum_univ_two]
  ring

/-
The variables below stand for finite derivative components in one row of the
capillary-stress divergence. The theorem checks only the polynomial collection
used after the product rules have already been stated.
-/
theorem capillary_divergence_collection_kernel
    (alpha beta gamma deltaK q lap alphaI gammaI betaJgJ deltaJhIJ
      hIJgJ rhoI lapI : Real) :
    q * alphaI - lap * gammaI + betaJgJ * rhoI - deltaJhIJ
      + 2 * alpha * hIJgJ + beta * hIJgJ + beta * rhoI * lap
      - gamma * lapI - deltaK * lapI =
    q * alphaI - lap * gammaI + betaJgJ * rhoI - deltaJhIJ
      + (2 * alpha + beta) * hIJgJ + beta * rhoI * lap
      - (gamma + deltaK) * lapI := by
  ring

theorem density_gradient_coefficient_map
    (coefficient massScale gradI gradJ : Real) :
    coefficient * (massScale * gradI) * (massScale * gradJ) =
      (coefficient * massScale ^ 2) * gradI * gradJ := by
  ring

theorem density_hessian_coefficient_map
    (coefficient massScale hessianIJ : Real) :
    coefficient * (massScale * hessianIJ) =
      (coefficient * massScale) * hessianIJ := by
  ring

theorem pressure_to_cauchy_force_bridge
    (body divP divSigma : Real)
    (hdiv : divSigma = -divP) :
    body - divP = body + divSigma := by
  rw [hdiv]
  ring

structure TensorForceComparison where
  literalTensorEquality : Prop
  divergenceEquality : Prop

def LiteralAndDivergenceMatch (comparison : TensorForceComparison) : Prop :=
  comparison.literalTensorEquality ∧ comparison.divergenceEquality

theorem divergence_match_not_literal_tensor_match
    (comparison : TensorForceComparison)
    (_hdiv : comparison.divergenceEquality)
    (hnotLiteral : ¬ comparison.literalTensorEquality) :
    ¬ LiteralAndDivergenceMatch comparison := by
  intro hmatch
  exact hnotLiteral hmatch.1

theorem dyadic_quadratic_nonnegative
    (coefficient gx gy : Real)
    (hcoefficient : 0 ≤ coefficient) :
    0 ≤ coefficient * (gx ^ 2 + gy ^ 2) := by
  positivity

#print axioms dyadic_gradient_stress_symmetric
#print axioms finite_stress_contraction_two_dim
#print axioms capillary_divergence_collection_kernel
#print axioms density_gradient_coefficient_map
#print axioms density_hessian_coefficient_map
#print axioms pressure_to_cauchy_force_bridge
#print axioms divergence_match_not_literal_tensor_match
#print axioms dyadic_quadratic_nonnegative

end Korteweg1901
