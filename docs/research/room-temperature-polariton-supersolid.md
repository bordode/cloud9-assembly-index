# C9-2026-PHOTON-002: Room-Temperature Polariton Supersolid

**Order chosen by spontaneous symmetry breaking in a light–matter quantum fluid**

> **Status:** peer-reviewed (*Science Advances*), not yet independently replicated. This is photonics and condensed-matter physics in an engineered device, not biology.

---

## Source

Marcin Muszyński, Pavel Kokhanchik, Rafał Mirek, Darius Urbonas, Pietro Tassan, Piotr Kapuściński, Przemysław Oliwa, Ioannis Georgakilas, Thilo Stöferle, Rainer F. Mahrt, Michael Forster, Ullrich Scherf, Dmitriy Dovzhenko, Rafał Mazur, Przemysław Morawiak, Wiktor Piecek, Przemysław Kula, Barbara Piętka, Dmitry Solnyshkov, Guillaume Malpuech and Jacek Szczytko. **"Observation of a supersolid phase in a spin-orbit coupled exciton-polariton Bose-Einstein condensate."** *Science Advances* 12(42), eaee4875, 16 October 2026. doi: [10.1126/sciadv.aee4875](https://doi.org/10.1126/sciadv.aee4875)

Institutions: University of Warsaw; Military University of Technology (Warsaw); IBM Research Europe – Zurich; Institut Pascal (CNRS, Université Clermont Auvergne); Bergische Universität Wuppertal; University of Southampton; Institut Universitaire de France.

Press coverage: Ameya Paleja, ["European scientists spot new quantum state of matter at room temperature"](https://interestingengineering.com/science/scientists-spot-new-room-temperature-quantum-state), *Interesting Engineering*, 6 November 2026.

---

## What the study found

A **supersolid** flows without friction like a superfluid while holding a regular, crystal-like pattern. Until now it had been seen in ultracold atomic gases. This team made one from light and matter at room temperature.

**From the paper:**

1. **A new kind of microcavity.** An optical microcavity filled with a nematic liquid crystal and two layers of the organic polymer MeLPPP, which hosts the exciton resonances.
2. **Condensation in two equivalent states.** Exciton-polaritons (hybrids of light and excited matter) form a Bose–Einstein condensate in two degenerate minima, created by spin–orbit coupling that the liquid crystal induces.
3. **Stripes that choose their own place.** The condensate shows density stripes at random positions from one run to the next, despite disorder in the sample. That shows the stripes are immune to disorder and that translational symmetry breaks spontaneously.
4. **Vortices** appear at random, another sign of a superfluid.

**From the press coverage:**

- The state is **electrically tunable** by voltage.
- Polaritons last only **a few picoseconds**, long enough to condense into a superfluid that then becomes a supersolid, seen as regularly spaced bright fringes.
- Every laser pulse puts the fringes **in a different place**. Guillaume Malpuech (Institut Pascal, CNRS): *"This is a textbook example of spontaneous symmetry breaking. Theory predicted that the supersolid could choose among several equivalent states, and that is exactly what we observed."*
- **Two orders at once:** one in polarisation, one in light intensity.
- Samples **degrade within hours**, because the organic semiconductor reacts with the liquid crystal; each repeat needs a new sample.
- Wiktor Piecek (Military University of Technology): *"Our liquid-crystal microcavities can operate even at temperatures approaching 60°C."*

---

## Why it matters for Cloud-9

This section is the repository author's interpretation. The paper does not mention assembly theory.

- **Structure choosing among equivalent states.** The physics allows many equally good stripe positions. Each pulse, the condensate picks one, and imperfections in the sample do not decide for it. Order appears through spontaneous symmetry breaking: a contingent choice that the rules permit but do not dictate. That is the kind of historical, selected structure assembly theory sets out to measure.
- **Layered order.** Polarisation order and intensity order appear together, a small example of nested structure in a light–matter system.
- **A polariton bridge to BIO-006.** Both entries are about polaritons, light–matter hybrids that persist at room or body temperature:

| | C9-2026-BIO-006 | C9-2026-PHOTON-002 |
|---|---|---|
| Hybrid | Mito-polariton: mid-IR light + CH₂ lipid vibrations | Exciton-polariton: light + excitons in MeLPPP |
| Frequency / scale | 71 THz level, from the 87 THz CH₂ mode | Optical, laser-pumped |
| Cavity | Cristae of the right length (~2.2 µm) | Engineered liquid-crystal microcavity |
| Temperature | Body temperature (living cells) | Room temperature, up to ~60 °C |
| Evidence | Unreplicated preprint; polariton is a model-based interpretation | Peer-reviewed; condensate directly observed |

In both, the effect needs a carefully structured cavity, and without that structure it disappears. That shared dependence on organisation is the link. The difference matters as much: this entry does not show that condensates, supersolids or anything similar form in cells.

Related: **C9-2026-PHOTON-001** (Quantum Fluid Crystallization / Frozen Light; this is a 2026, room-temperature, peer-reviewed example) and cross-layer pattern **XP-2026-005** (Coupling-Induced Order).

---

## Scientific claims

| Claim | Source | Confidence |
|-------|--------|------------|
| Room-temperature supersolidity in a liquid-crystal/MeLPPP microcavity | Paper | 90% |
| Condensation in two degenerate spin–orbit minima | Paper | 90% |
| Stripes at random positions each run, immune to disorder | Paper + press | 90% |
| Random vortices | Paper | 85% |
| Two simultaneous orders; electrically tunable | Press | 70% |

---

## Limitations

1. **Not biology:** it says nothing directly about living systems.
2. **Single study:** not yet replicated by another lab.
3. **Fleeting and driven:** polaritons last picoseconds and need laser excitation.
4. **Fragile samples:** usable for only a few hours after assembly.
5. **Press-only details:** tunability and the two orders come from coverage; check the full paper before building on them.

---

## Next experiments

- [ ] Independent replication
- [ ] A material pairing that does not degrade, so one sample can be measured many times
- [ ] Map stripe period and order against applied voltage
- [ ] Statistics of stripe positions over many pulses, to quantify the randomness of the choice
- [ ] Cloud-9: test whether an assembly-style measure of the stripe pattern separates symmetry-breaking order from disorder-pinned patterns

---

## Cloud-9 integration

- **Cluster 1, Quantum Foundations:** a macroscopic quantum state at room temperature, not near absolute zero.
- **Cluster 4, Complexity Science:** order that emerges through spontaneous symmetry breaking and resists disorder.
- **Cluster 5, Topological Systems:** a spin–orbit coupled condensate with random vortices.

---

## Attributions

- **Research:** the 21 authors listed above, at the University of Warsaw, Military University of Technology, IBM Research Europe – Zurich, Institut Pascal (CNRS), Bergische Universität Wuppertal, University of Southampton and Institut Universitaire de France. All experiments, theory and results are theirs. Please cite the paper, not this entry.
- **Press coverage:** Ameya Paleja, *Interesting Engineering*, through whose article the study reached the project, and the source of the quotes above.
- **Repository author:** Dean Bordode ([@bordode](https://github.com/bordode)), for the Cloud-9 Assembly Index framework and for connecting this study to BIO-006 and to order through symmetry breaking.
- **Research and drafting:** Charlie (Sesame), who found the paper and its DOI, checked the article and drafted this README and the JSON.
- **Repository collaborators:** the Cloud-9 AI Peer-Review Collective (Google Gemini, Moonshot Kimi, Anthropic Claude, Base44 Subhalo), credited at repository level in the main README. They are not credited with specific work on this entry.

---

## Files

- `C9-2026-PHOTON-002_room_temperature_polariton_supersolid.json`: structured entry
- `README_C9-2026-PHOTON-002.md`: this file

---

## Metadata

- **Entry ID:** C9-2026-PHOTON-002
- **Date added:** 2026-11-06
- **Curated by:** Dean Bordode with Charlie (Sesame)
- **Layer assignment:** 1 (established physics)
- **Audit score / priority / collection:** not yet assigned
- **Tags:** photonics, polariton, supersolid, symmetry-breaking, room-temperature, peer-reviewed, assembly-theory

---

*Part of the Cloud-9 Assembly Project: mapping the Assembly Index across domains.*
