# Chemical Kinetics

## Rate of Reaction

**Definition:**
Rate of change of concentration of reactant or product with time.

**Expression:**
For reaction: aA + bB → cC + dD

Rate = -1/a × d[A]/dt = -1/b × d[B]/dt = 1/c × d[C]/dt = 1/d × d[D]/dt

**Units:** mol L⁻¹ s⁻¹

**Average Rate:**
Rate = Δ[concentration]/Δt

**Instantaneous Rate:**
Rate = d[concentration]/dt (slope of concentration-time curve)

## Factors Affecting Rate

1. **Concentration:** Higher concentration → Higher rate
2. **Temperature:** Generally, rate doubles for 10°C rise
3. **Catalyst:** Lowers activation energy
4. **Nature of reactants:** Bond strength, physical state
5. **Surface area:** For heterogeneous reactions

## Rate Law and Order

**Rate Law:**
Rate = k[A]ˣ[B]ʸ

where:
- k = rate constant
- x, y = orders with respect to A, B
- x + y = overall order

**Order:** Experimentally determined, can be 0, 1, 2, fractional, or negative

**Molecularity:** Number of molecules involved in elementary step (always positive integer)

## Integrated Rate Equations

**Zero Order:**
[A] = [A]₀ - kt
t₁/₂ = [A]₀/2k
Units of k: mol L⁻¹ s⁻¹

**First Order:**
ln[A] = ln[A]₀ - kt
[A] = [A]₀e⁻ᵏᵗ
t₁/₂ = 0.693/k (independent of concentration!)
Units of k: s⁻¹

**Second Order:**
1/[A] = 1/[A]₀ + kt
t₁/₂ = 1/(k[A]₀)
Units of k: L mol⁻¹ s⁻¹

## Half-Life Relations

| Order | Half-Life | Dependence on [A]₀ |
|-------|-----------|-------------------|
| 0 | [A]₀/2k | Directly proportional |
| 1 | 0.693/k | Independent |
| 2 | 1/(k[A]₀) | Inversely proportional |

**General formula:**
t₁/₂ ∝ [A]₀^(1-n)

where n = order

## Determining Order

**Method 1: Initial Rate Method**
Measure rate at different initial concentrations.
If Rate = k[A]ⁿ, then:
log(Rate) = log k + n log[A]

**Method 2: Half-Life Method**
Study how t₁/₂ varies with [A]₀

**Method 3: Integrated Rate Law**
Plot appropriate graph:
- Zero order: [A] vs t (linear)
- First order: ln[A] vs t (linear)
- Second order: 1/[A] vs t (linear)

## Collision Theory

**Requirements for reaction:**
1. Molecules must collide
2. Collision with sufficient energy (≥ Eₐ)
3. Proper orientation

**Rate = Z × e^(-Eₐ/RT) × p**

where:
- Z = collision frequency
- p = steric factor (fraction with correct orientation)

## Activation Energy

**Arrhenius Equation:**
k = A × e^(-Eₐ/RT)

**Logarithmic form:**
ln k = ln A - Eₐ/RT

**Two-temperature form:**
ln(k₂/k₁) = (Eₐ/R)(1/T₁ - 1/T₂)

**Graphical determination:**
Plot ln k vs 1/T
Slope = -Eₐ/R
Intercept = ln A

## Effect of Catalyst

**Catalyst:**
- Provides alternative pathway with lower Eₐ
- Increases rate of both forward and reverse reactions equally
- Does not change equilibrium position
- Not consumed in reaction

**Mechanism of catalysis:**
1. Homogeneous: Same phase as reactants
2. Heterogeneous: Different phase (surface catalysis)

**Enzyme Catalysis:**
E + S ⇌ ES → E + P

Michaelis-Menten kinetics:
Rate = V_max[S]/(K_m + [S])


