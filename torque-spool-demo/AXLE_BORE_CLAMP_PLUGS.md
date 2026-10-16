# Hollow screw-together axle-bore sleeve caps

`Axle_Bore_Clamp_Plugs_print_1set.stl` contains one male cap and one female cap in a single print-ready file. Each part is a hollow cup with a thin annular sleeve that follows the original spool's axle-bore wall. The sleeves thread together near the center of the assembled spool while thick outside flanges seal the two ends.

There is no solid center rod. Lead shot occupies the hollow axial core inside the sleeves, keeping most of the added mass close to the rotation axis.

## Source dimensions and final design

The original OpenSCAD source and supplied meshes specify a 36.0 mm through-bore and 112.0 mm between the assembled outside wheel faces.

| Feature | Final dimension |
|---|---:|
| Nominal spool bore | 36.0 mm diameter |
| Sleeve outside | 35.4 mm diameter |
| Nominal radial fit clearance | 0.30 mm |
| Main sleeve inside | 30.0 mm diameter |
| Main sleeve wall | 2.7 mm |
| Minimum continuous shot passage | 23.8 mm diameter |
| Sealed outside end wall | 3.0 mm thick |
| Stop flanges | 44.0 mm diameter × 5.0 mm thick |
| Male thread | 30.0 mm major diameter, 3.5 mm pitch |
| Male threaded-tube minimum wall | 2.0 mm |
| Female groove minimum wall | 1.9 mm |
| Sleeve reach from each wheel face | 66.0 mm |
| Seated sleeve overlap | 20.0 mm |
| Seated threaded engagement | 18.5 mm (about 5.3 turns) |

The current geometry leaves approximately 79.0 cm³, or 69% of the nominal through-bore volume, available as internal void. Actual shot capacity is lower because spherical shot does not pack without gaps. The passage is 30.0 mm across for most of its length and narrows only through the short threaded overlap.

The dodecagonal flange edges provide a hand grip. The generator verifies the complete screw path as well as the final seated position. The current STL has two watertight, consistently wound bodies with no calculated interference throughout engagement.

## Printing

- Preferred material: tough or ABS-like solid resin. Do not use brittle standard resin.
- The hollow cups can create resin suction if printed flat. Angle each part roughly 30–45° with its open sleeve end facing partly downward so uncured resin can drain.
- Put supports on the outside flange and smooth sleeve surfaces where possible. Keep support tips off the mating threads.
- Do not apply the slicer's automatic hollowing operation; the CAD model already contains the required hollow interior and sealed end wall.
- Fully drain, wash, and post-cure both internal passages before adding shot.

## Dry fit and filling

1. Assemble the empty spool halves normally.
2. Insert the two empty caps from opposite outside faces and start the thread by hand.
3. Confirm that both flanges seat without forcing or cross-threading, then remove both caps.
4. Stand the spool vertically over a tray and insert the male cap into the lower end.
5. Add clean, dry shot through the upper bore. The shot will fill the lower cup and the central passage.
6. For maximum fill, separately fill the female cup, hold a thin card over its open end, invert it over the upper bore, and withdraw the card as the sleeve enters. Some headspace is advisable so the shot does not jam the threads.
7. Engage the female sleeve and tighten the two dodecagonal flanges only finger-snug.
8. Shake and inspect the completed spool over a tray before classroom use.

Perform the first assembly without lead. Resin dimensions vary with exposure and cure, and a dry fit is far easier to correct.

## Fit tuning

- Sleeve too tight in the spool: reduce `sleeve_outer_diameter_mm` from 35.4 to 35.2 mm.
- Thread too tight: increase `female_thread_minor_diameter_mm` and `female_thread_major_diameter_mm` by 0.15–0.20 mm.
- Thread too loose: reduce those two female diameters in 0.10 mm steps.
- Do not reduce the 3.0 mm sealed end wall, 2.0 mm male threaded-tube wall, or 1.9 mm minimum female groove wall.

Regenerate the STL, validation record, and preview by running:

    python .\generate_axle_bore_clamp_plugs.py

## Lead and mechanical safety

Lead is toxic. Wear disposable gloves, avoid dust, wash hands afterward, and keep the filled spool away from children and food-preparation areas. Printed resin threads are not certified hazardous-material containment. Inspect the flanges, sleeve roots, and threads before every use. Do not overtighten, drop, or throw the weighted spool. For permanent classroom containment, add a compatible secondary seal after verifying the dry fit. Dispose of lead and contaminated cleanup materials according to local regulations.
