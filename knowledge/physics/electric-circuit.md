---
id: electric-circuit
type: apparatus
title: Electric Circuit & Ohm's Law Verification Setup
description: Closed conducting loop comprising a DC power source, plug key switch, ammeter in series, voltmeter in parallel, rheostat, and nichrome resistor wire.
status: active
verified: human-reviewed
timestamp: "2026-08-28T00:00:00Z"
resource: assets/physics/full-circuit
tags: [apparatus, physics, electricity, ohms-law, resistance, circuit]
sources:
  - name: NCERT Class 10 Science
    chapter: "Chapter 12: Electricity"
    activity: "Activity 12.1"
    section: "12.2 Ohm's Law"
cbse_mapping:
  class: 10
  subject: physics
  chapter: "Electricity"
  ncert_activity: "Activity 12.1"
  key_takeaways:
    - "Ammeter is always connected in series because it has low internal resistance to measure total current I."
    - "Voltmeter is always connected in parallel across the resistor because it has high internal resistance to measure potential difference V."
    - "Ohm's Law states V is directly proportional to I at constant temperature (V = IR)."
equations:
  - latex: "V = I \\cdot R"
    meaning: "Ohm's Law: Potential difference V across conductor equals electric current I multiplied by resistance R."
    type: physical
  - latex: "R = \\rho \\frac{l}{A}"
    meaning: "Resistance formula in terms of electrical resistivity rho, length l, and cross-sectional area A."
    type: physical
safety:
  - "Ensure key is inserted only while taking readings to prevent resistor heating and resistance drift."
related_assets:
  - full-circuit
  - ammeter
  - voltmeter
  - resistor
  - rheostat
  - battery
  - switch
---

# Electric Circuit & Ohm's Law Apparatus

Standard CBSE Class 10 electricity setup for verifying the linear $V-I$ characteristic of metallic conductors. By varying the position of the rheostat sliding contact, students record multiple current-voltage pairs to plot a straight-line graph through the origin, whose slope represents the ohmic resistance $R = \Delta V / \Delta I$.
