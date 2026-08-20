#!/usr/bin/env bash
# Rebuild and audit the target-local finite Lean kernels.
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
FORMAL="$ROOT/formal/korteweg1901_mathlib"
MODULE="$FORMAL/Korteweg1901/TensorKernels.lean"

if ! command -v lake >/dev/null 2>&1; then
  printf '%s\n' 'FORMAL_VERIFY_FAIL lake is not available on PATH' >&2
  exit 2
fi

if grep -RInE '\b(sorry|admit)\b|^[[:space:]]*axiom[[:space:]]' \
  "$FORMAL/Korteweg1901" --include='*.lean'; then
  printf '%s\n' 'FORMAL_VERIFY_FAIL prohibited placeholder or custom axiom found' >&2
  exit 1
fi

(
  cd "$FORMAL"
  # Name the public module explicitly: a bare `lake build` may only resolve
  # package configuration in a dependency-hydrated standalone tree.
  lake build Korteweg1901.TensorKernels
)

for theorem in \
  dyadic_gradient_stress_symmetric \
  finite_stress_contraction_two_dim \
  capillary_divergence_collection_kernel \
  density_gradient_coefficient_map \
  density_hessian_coefficient_map \
  pressure_to_cauchy_force_bridge \
  divergence_match_not_literal_tensor_match \
  dyadic_quadratic_nonnegative
do
  grep -q "theorem $theorem" "$MODULE"
done

printf '%s\n' 'FORMAL_VERIFY_OK theorems=8 scope=finite_kernels_only'
