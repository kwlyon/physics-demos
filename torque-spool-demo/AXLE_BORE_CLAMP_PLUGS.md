# Rigid screw-together axle-bore plugs

Axle_Bore_Clamp_Plugs_print_1set.stl contains one male cap and one female cap in a single print-ready file. The caps enter opposite ends of the original spool's central through-bore and screw together internally. Their outside flanges clamp against the two wheel faces, so friction is not the primary retention mechanism.

## Source dimensions and final design

The original OpenSCAD source and supplied meshes specify a 36.0 mm through-bore and 112.0 mm between the assembled outside wheel faces.

| Feature | Final dimension |
|---|---:|
| Nominal spool bore | 36.0 mm diameter |
| Rigid guide shanks | 35.4 mm diameter × 14.0 mm long |
| Stop flanges | 44.0 mm diameter × 5.0 mm thick |
| Male stem root | 10.8 mm diameter |
| Female receiver outside | 21.0 mm diameter |
| Printed thread | 13.0 mm nominal major diameter, 3.5 mm pitch |
| Stem reach from each wheel face | 66.0 mm |
| Seated stem overlap | 20.0 mm |
| Seated threaded engagement | 17.0 mm (about 4.9 turns) |

The dodecagonal flange edges provide a hand grip. The guide shanks are a sliding fit with 0.30 mm nominal radial clearance and tapered tips for alignment. The coarse thread has enlarged female clearances for rigid-resin printing.

The generator verifies the complete screw path as well as the final seated position. The current STL has two watertight, consistently wound bodies and stays below 0.1 mm³ of numerical mesh contact throughout engagement; that residual is at the tessellation scale rather than a designed interference.

## Printing

- Preferred material: tough or ABS-like solid resin. Do not use brittle standard resin.
- Print both caps with the broad outside flanges flat on the build plate and the stems pointing upward.
- If printing directly on the plate, compensate for elephant foot so the flange edges remain easy to grip.
- If supports are required, raise both parts together, keep the stems vertical, and support the flange perimeter uniformly.
- Fully wash, drain, and post-cure both parts. Pay special attention to the blind female thread.

## Dry fit and assembly

1. Assemble and screw together the empty male and female spool halves first.
2. Insert the male clamp cap through one outside wheel face.
3. Insert the female cap through the opposite face and turn its dodecagonal flange while holding the male flange.
4. Confirm that the threads start easily by hand and both flanges can seat. Never force or cross-thread resin parts.
5. Unscrew and remove the female cap while leaving the male cap in place.
6. Stand the remaining open end upward and add clean, dry lead shot around the central male stem.
7. Leave enough headspace for the female receiver stem.
8. Reinsert the female cap, engage the thread, and tighten only finger-snug until both flanges seat.
9. Shake and inspect the spool over a tray before classroom use.

## Fit tuning

Rigid-resin dimensions vary with exposure, washing, and cure.

- Thread too tight: increase female_thread_minor_diameter_mm and female_thread_major_diameter_mm by 0.15–0.25 mm.
- Thread too loose: reduce those two female diameters in 0.10 mm steps.
- Guide shank too tight in the spool: reduce guide_shank_diameter_mm from 35.4 to 35.2 mm.
- Do not reduce the 5.0 mm flange thickness, 10.8 mm male root, or 3.1 mm minimum female thread wall.

Regenerate the STL, validation record, and preview by running:

    python .\generate_axle_bore_clamp_plugs.py

## Lead and mechanical safety

Lead is toxic. Wear disposable gloves, avoid dust, wash hands afterward, and keep the filled spool away from children and food-preparation areas. Printed resin threads are not certified hazardous-material containment. Inspect the flanges, stem roots, and threads before every use. Do not overtighten, drop, or throw the weighted spool. For permanent classroom containment, add a compatible secondary seal after verifying the dry fit. Dispose of lead and contaminated cleanup materials according to local regulations.
