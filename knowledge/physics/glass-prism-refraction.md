---
id: glass-prism-refraction
type: experiment
title: Refraction of Light Through a Triangular Glass Prism
description: Experimental demonstration of angular deviation and chromatic dispersion when a collimated light ray traverses non-parallel refracting boundaries of an optical prism.
status: active
verified: human-reviewed
timestamp: "2026-08-28T00:00:00Z"
resource: assets/physics/glass-prism-refraction
tags: [physics, optics, refraction, prism, dispersion, cbse-class-10]
sources:
  - name: NCERT Class 10 Science
    chapter: "Chapter 11: The Human Eye and the Colourful World"
    activity: "Activity 11.2"
    section: "11.2 Refraction of Light through a Prism"
cbse_mapping:
  class: 10
  subject: physics
  chapter: "The Human Eye and the Colourful World"
  ncert_activity: "Activity 11.2"
  key_takeaways:
    - "Because refracting lateral surfaces of a prism are inclined at angle A (60°), the emergent ray is not parallel to the incident ray."
    - "Universal Prism Law: A + D = i + e (Angle of Prism + Angle of Deviation = Angle of Incidence + Angle of Emergence)."
    - "At minimum deviation (Dm), the internal refracted ray travels strictly parallel to the prism base."
equations:
  - latex: "\\angle A + \\angle D = \\angle i + \\angle e"
    meaning: "The sum of the angle of the prism (A) and the angle of deviation (D) equals the sum of the angle of incidence (i) and the angle of emergence (e)."
    type: physical
  - latex: "n = \\frac{\\sin\\left(\\frac{A + D_m}{2}\\right)}{\\sin\\left(\\frac{A}{2}\\right)}"
    meaning: "Prism formula relating refractive index n to apex angle A and minimum angle of deviation Dm."
    type: physical
misconceptions:
  - claim: "Light passing through a prism behaves exactly like light passing through a rectangular glass slab."
    correction: "In a rectangular slab with parallel faces, light undergoes lateral displacement without angular deviation. In a prism with inclined faces, light undergoes net angular deviation (D)."
related_assets:
  - glass-prism-refraction
  - glass-prism
  - glass-slab
related_lessons:
  - physics.glass-prism-refraction
related_concepts:
  - optical-prism
  - angle-of-deviation
  - optical-dispersion
  - snells-law
---

# Refraction of Light Through a Triangular Glass Prism

## 1. Pedagogical Overview
When a ray of light enters an equilateral triangular glass prism ($A = 60^\circ$):
1. **At first face $AB$ (Air $\rightarrow$ Glass)**: Light enters an optically denser medium ($n \approx 1.517$) and refracts towards the normal ($r_1 < i$).
2. **Inside the prism along $EF$**: The ray propagates through the bulk glass.
3. **At second face $AC$ (Glass $\rightarrow$ Air)**: Light exits into the optically rarer air and refracts away from the second normal ($e > r_2$).
4. **Deviation Angle ($D$)**: Extending the forward incident ray and backward emergent ray reveals the net angular deviation subtended at vertex $G$.

## 2. Planar Interface Ray Vector Dynamics
At each refracting boundary with outward surface normal $\mathbf{n}$ and incident ray direction unit vector $\mathbf{d}_1$:
- **Snell's Law in Vector Form**:
  $$\mathbf{d}_2 = \frac{n_1}{n_2}\mathbf{d}_1 + \left(\frac{n_1}{n_2}\cos\theta_1 - \cos\theta_2\right)\mathbf{n}$$
  where $\cos\theta_1 = -(\mathbf{d}_1 \cdot \mathbf{n})$ and $\cos\theta_2 = \sqrt{1 - \left(\frac{n_1}{n_2}\right)^2(1 - \cos^2\theta_1)}$.
- **Total Internal Reflection Boundary Check**:
  When transitioning from denser glass ($n_1 \approx 1.517$) to rarer air ($n_2 \approx 1.0$), the critical angle is $\theta_c = \arcsin(n_2 / n_1) \approx 41.2^\circ$. If the internal incidence angle $r_2 > \theta_c$, the radicand becomes negative; the transmitted refracted branch ceases to exist, and total internal reflection occurs.
