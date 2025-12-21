# Continuity and Differentiability

## Definition of Derivative

The derivative of a function f(x) at point x is defined as:

**Formula:**
f'(x) = lim[h→0] (f(x+h) - f(x)) / h

**Interpretation:**
- Geometrically: Slope of tangent at point x
- Physically: Instantaneous rate of change

## Standard Derivatives

**Power Functions:**
- d/dx(xⁿ) = nxⁿ⁻¹
- d/dx(1/x) = -1/x²
- d/dx(√x) = 1/(2√x)

**Exponential and Logarithmic:**
- d/dx(eˣ) = eˣ
- d/dx(aˣ) = aˣ ln(a)
- d/dx(ln x) = 1/x
- d/dx(logₐ x) = 1/(x ln a)

**Trigonometric:**
- d/dx(sin x) = cos x
- d/dx(cos x) = -sin x
- d/dx(tan x) = sec²x
- d/dx(cot x) = -csc²x
- d/dx(sec x) = sec x tan x
- d/dx(csc x) = -csc x cot x

**Inverse Trigonometric:**
- d/dx(sin⁻¹x) = 1/√(1-x²)
- d/dx(cos⁻¹x) = -1/√(1-x²)
- d/dx(tan⁻¹x) = 1/(1+x²)

## Differentiation Rules

**Sum/Difference Rule:**
d/dx(f ± g) = f' ± g'

**Product Rule:**
d/dx(f·g) = f'·g + f·g'

**Quotient Rule:**
d/dx(f/g) = (f'·g - f·g') / g²

**Chain Rule:**
d/dx[f(g(x))] = f'(g(x)) · g'(x)

**Implicit Differentiation:**
When y is defined implicitly by F(x,y) = 0, differentiate both sides with respect to x, treating y as a function of x.

## Applications of Derivatives

**Finding Maxima and Minima:**
1. Find f'(x) = 0 (critical points)
2. Use second derivative test:
   - f''(x) > 0 → local minimum
   - f''(x) < 0 → local maximum
   - f''(x) = 0 → inconclusive

**Rate of Change:**
If y = f(x), then dy/dx represents the rate of change of y with respect to x.

**Tangent and Normal:**
- Slope of tangent at (a, f(a)): m = f'(a)
- Equation of tangent: y - f(a) = f'(a)(x - a)
- Slope of normal: -1/f'(a)
