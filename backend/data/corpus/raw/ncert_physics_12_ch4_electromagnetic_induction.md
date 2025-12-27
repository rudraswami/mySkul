# Electromagnetic Induction

## Magnetic Flux

Magnetic flux is the number of magnetic field lines passing through a surface.

**Formula:**
Φ = B·A = BA cos θ

where θ = angle between B and normal to surface

**Units:** Weber (Wb) = T·m²

## Faraday's Laws of Electromagnetic Induction

**First Law:**
Whenever magnetic flux linked with a circuit changes, an EMF is induced.

**Second Law:**
The induced EMF is equal to the negative rate of change of magnetic flux.

**Formula:**
ε = -dΦ/dt

For N turns: ε = -N(dΦ/dt)

## Lenz's Law

The induced current flows in a direction such that it opposes the change that produces it.

**Applications:**
- Conservation of energy
- Determines direction of induced current
- Explains the negative sign in Faraday's law

**Examples:**
- Magnet approaching coil: induced current creates repelling field
- Magnet receding: induced current creates attracting field

## Motional EMF

EMF induced in a conductor moving through a magnetic field.

**For rod of length L moving with velocity v perpendicular to B:**
ε = BLv

**General form:**
ε = ∮(v × B)·dl

**Direction:** Use right-hand rule or Lenz's law

## Eddy Currents

Induced currents in bulk conductors when flux changes.

**Effects:**
- Heating (I²R losses)
- Damping of motion
- Electromagnetic braking

**Applications:**
- Induction heating
- Electric brakes
- Speedometers
- Induction cookers

**Reduction:** Use laminated cores to reduce path for eddy currents

## Self-Inductance

Property of a coil that opposes change in current through it.

**Self-induced EMF:**
ε = -L(dI/dt)

where L = self-inductance (Henry, H)

**Inductance of Solenoid:**
L = μ₀n²AL = μ₀N²A/L

where:
- n = N/L = turns per unit length
- A = cross-sectional area
- L = length of solenoid

**Energy Stored in Inductor:**
U = ½LI²

## Mutual Inductance

Flux linkage in one coil due to current in another.

**Mutual induced EMF:**
ε₂ = -M(dI₁/dt)

**For two solenoids:**
M = μ₀n₁n₂AL

**Coefficient of Coupling:**
k = M/√(L₁L₂)

For perfect coupling: k = 1, M = √(L₁L₂)

## AC Generator

Converts mechanical energy to electrical energy.

**Principle:** Electromagnetic induction

**EMF produced:**
ε = ε₀ sin(ωt)

where ε₀ = NABω = peak EMF

**Average EMF (half cycle):** ε_avg = 2ε₀/π

**RMS EMF:** ε_rms = ε₀/√2

## Transformer

Transfers electrical energy between circuits through mutual induction.

**Transformation Ratio:**
N_s/N_p = V_s/V_p = I_p/I_s

**Step-up:** N_s > N_p (increases voltage)
**Step-down:** N_s < N_p (decreases voltage)

**Efficiency:**
η = (Output power)/(Input power) × 100%

**Energy Losses:**
1. Copper losses (I²R in windings)
2. Iron losses (eddy currents, hysteresis)
3. Flux leakage
4. Magnetostriction


