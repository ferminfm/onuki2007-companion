import Lake
open Lake DSL

package korteweg1901_mathlib where

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "v4.29.0"

@[default_target]
lean_lib Korteweg1901 where
  roots := #[`Korteweg1901.TensorKernels]
