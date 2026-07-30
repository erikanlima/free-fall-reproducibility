# Experimental acquisition protocol

The measurements were obtained in one experimental campaign using the same free-fall apparatus throughout.

## Apparatus

- electromagnet and support structure
- metallic sphere, diameter 6.35 mm
- photogate 1
- photogate 2
- digital timing unit

## One experimental run

1. The vertical separation between photogate 1 and photogate 2 was set to a selected value `H`.
2. The lower surface of the 6.35 mm sphere was positioned approximately 1 mm above the beam level of photogate 1.
3. The sphere was released and fell through the two photogates.
4. The timer started at the onset of beam interruption, when the lower surface of the sphere first reached the beam of photogate 1.
5. The timer stopped at the corresponding onset of beam interruption at photogate 2.
6. The timing unit displayed one elapsed transit time `t` for the motion between the two photogates.
7. One pair `(H, t)` was recorded for that release.

The apparatus did not record several time intervals during the same fall. Each row in the dataset corresponds to a new sphere release.

## Acquisition blocks

- **Block 1:** 75 releases.
- The photogate separation was then reset to a lower value.
- **Block 2:** 44 additional releases.

The same sphere, photogates, timing unit, support, and release apparatus were used in both blocks. The block labels describe the sequential acquisition structure and the reset of `H`; they do not indicate different instruments or different experimental setups.

Within each block, `H` increased monotonically with acquisition order. Therefore, the dataset cannot separate a dependence on `H` from order-dependent effects such as apparatus warm-up, timing drift, alignment changes, release variability, or effects associated with repositioning the photogates between blocks.

## Trigger geometry

The photogates triggered at the beginning of beam interruption. Therefore, the nominal pre-trigger fall distance is the approximately 1 mm clearance between the lower surface of the sphere and the beam of photogate 1. The sphere diameter (6.35 mm) is not added to this distance. Using the geodetic comparison value of gravity gives a nominal geometric entry velocity of approximately 0.140 m/s. The clearance and trigger threshold were not calibrated with a quantified uncertainty. The value is therefore used first as an independent physical check. A separate nominal-geometry sensitivity fit fixes `h0 = 1 mm` to test whether that geometry alone can describe the measurements; it is not treated as a calibrated primary estimate of gravity.
