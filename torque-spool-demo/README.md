# Plug-together spool-paradox inserts

This directory contains five reusable, two-piece insert sets for the supplied spool. Each set plugs together around the existing 78 mm diameter winding drum without disassembling the spool. Half A carries the replacement string anchor, anti-rotation keys, and four plain tapered alignment plugs; half B carries four matching sockets. There are no hooks, flexible latches, or snap detents. The wound cord supplies retention.

It also includes two low-profile rope-hook accessories. Their tapered J-shaped noses thread beside the recessed anchor post and rotate around it; the tangent tail then lies back against the winding surface. A raised 5.2 mm eyelet on the tail provides an easier place to tie the rope. Use the 6.2 mm-post hook for the original spool and the 30°/40°/45°/50° inserts, and the 4.0 mm-post hook for the thinner 60° insert. See `ROPE_HOOK.md` for installation and printing details.

## Physics and final sizes

With both supplied TPU tires installed, the measured outer rolling-wheel diameter is **185.0 mm**, giving an outer rolling radius of **92.5 mm**.

### Predicting the critical angle

Let `D` be the outside diameter of the tire, `R = D/2` the rolling radius, `r` the winding radius, and `theta_c` the critical pull angle measured above horizontal. At the critical angle, the cord's line of action passes through the spool's contact point with the floor. The pull therefore produces no torque about that contact point. The geometry gives

```text
r = R cos(theta_c)

theta_c = cos^-1(r/R) = cos^-1(2r/D)
```

Below this angle the spool rolls one way; above it, the torque reverses and the spool rolls the other way. For the most precise experimental prediction, `r` is the radius to the cord's centerline rather than merely the bare insert surface. The labeled insert sizes use the surface-radius convention described below.

### Worked check: 45° insert

For the 45° insert, the tire-on outside diameter is `D = 185.0 mm`, so `R = 92.5 mm`. The designed winding-surface radius is `r = 65.407 mm` (a winding diameter of `130.815 mm`). Substitution gives

```text
theta_c = cos^-1(r/R)
        = cos^-1(65.407 mm / 92.5 mm)
        = 45.00 degrees
```

Thus the modeled dimensions reproduce the nominal 45° critical angle before correcting for cord thickness.

### Designed insert sizes

| Label | Designed surface radius | Diameter | Nominal shell thickness | Plastic-flange clearance |
|---:|---:|---:|---:|---:|
| 30° | 80.107 mm | 160.215 mm | 40.857 mm | 9.893 mm |
| 40° | 70.859 mm | 141.718 mm | 31.609 mm | 19.141 mm |
| 45° | 65.407 mm | 130.815 mm | 26.157 mm | 24.593 mm |
| 50° | 59.458 mm | 118.916 mm | 20.208 mm | 30.542 mm |
| 60° | 46.250 mm | 92.500 mm | 7.000 mm | 43.750 mm |

Every half now carries the identification twice:

- The broad, flat mating edge retains the full one-line label, for example `50° FROM HORIZONTAL | r=59.5 mm`. This bold lettering is 4.8 mm high and recessed 2.0 mm.
- The curved outside carries a much larger two-line label: `50° FROM HORIZONTAL` over `r = 59.5 mm`. These letters are 12 mm high, wrap over as much as 150° of the half-cylinder, and are recessed 0.8 mm. Both A and B halves of all five angle sets have the exterior marking.

The shallow exterior recess leaves the exact nominal winding radius on all surrounding surface areas. A taut cord bridges the small engraved strokes; for the cleanest physics demonstration, begin the working wrap on an unengraved portion of the cylinder.

### Cord-centerline convention

The labels refer to the physical cylinder surface, as requested. For a cord of diameter `d`, the first-layer cord-centerline radius is approximately `r + d/2`. Thus a 2.0 mm cord would shift the ideal angles to approximately 28.74°, 39.03°, 44.12°, 49.19°, and 59.28°. Additional winding layers increase the effective radius further. Use a thin single layer when demonstrating the labeled values.

## Printing

- Preferred material: PETG or PLA. The revised joints do not rely on material flexure.
- Nozzle: 0.4 mm.
- Layer height: 0.20 mm; 0.16 mm gives especially clean engraved lettering and plug surfaces.
- Walls: 4 perimeters minimum.
- Top/bottom layers: 5.
- Infill: 20–30% gyroid or cubic.
- Orientation: stand each half on either 91 mm axial end face, with a brim. This keeps the winding cylinder vertical and dimensionally round.
- Supports: the shell and anchor are support-free in that orientation. Use build-plate-only or painted support just beneath the four 5.0 mm horizontal plugs on half A if the printer does not bridge them cleanly. Half B normally needs no support.
- Elephant-foot compensation: 0.15–0.20 mm is helpful on the axial end touching the plate.

## Assembly and removal

1. Identify half A by its recessed string bay and post.
2. Place half A on the +Y/string-anchor side of the spool. Align its two small internal keys with the unused side strips of the original 22 mm-wide anchor bay.
3. Bring half B in radially from the opposite side.
4. Align all four tapered plugs with their flared sockets and push the halves straight together until the mating edges are evenly seated. Nothing needs to click.
5. Push the cord through the narrow outer entry beside the captive post, seat it in the larger space behind the post, and wind in the natural tangential direction.
6. To remove the insert, unwrap the cord and pull the halves straight apart near their axial ends. Do not lever directly on the string post.

The 4.2 mm plug bases enter 4.6 mm sockets, providing 0.20 mm radial clearance (0.40 mm diametral). Plug tips taper to 3.6 mm and each socket has a 5.1 mm flared lead-in, making alignment easy. The sockets are 0.35 mm deeper than the 5.0 mm plugs, and the 0.30 mm shell seam stays clear when assembled.

## Fit tuning

All fit controls are near the top of `generate_spool_inserts.py`.

- Drum fit too tight: increase `radial_clearance` from 0.25 to 0.35 mm.
- Drum fit too loose: reduce it toward 0.15–0.20 mm.
- Plugs too tight: increase `plug_socket_radius` from 2.30 to 2.35–2.40 mm.
- Plugs too loose: reduce `plug_socket_radius` in 0.05 mm steps, but keep at least 0.10 mm radial clearance for ordinary FDM printing.
- Seams fuse or rub: increase `seam_gap` from 0.30 to 0.40 mm.

Regenerate all parts after changing a parameter:

```powershell
python .\generate_spool_inserts.py
python .\validate_spool_inserts.py
python .\render_spool_inserts.py
```

The generator requires Python with `numpy`, `trimesh`, `manifold3d`, and `matplotlib`.

## Files

- `Spool_Insert_30deg_A.stl` / `B.stl`
- `Spool_Insert_40deg_A.stl` / `B.stl`
- `Spool_Insert_45deg_A.stl` / `B.stl`
- `Spool_Insert_50deg_A.stl` / `B.stl`
- `Spool_Insert_60deg_A.stl` / `B.stl`
- `Low_Profile_Rope_Hook_6p2mm_Post.stl`
- `Low_Profile_Rope_Hook_4p0mm_Post.stl`
- `generate_spool_inserts.py` — editable parametric CAD source.
- `generate_rope_hook.py` — editable source, validation, and preview generator for the hook accessories.
- `validate_spool_inserts.py` — independent validation of exported STLs and source-spool intersections.
- `render_spool_inserts.py` — reproducible inspection renders.
- `DIMENSIONAL_INSPECTION.md` — measured source geometry and anchor analysis.
- `VALIDATION.md` and `validation_report.json` — human-readable and machine-readable results.
- `design_manifest.json` — exact dimensions, labels, and part metadata.
- `ROPE_HOOK.md` and `rope_hook_validation.json` — hook instructions and generated mesh checks.
- `Spool_Paradox_Bambu_Print_Kit/` — the original supplied spool STLs, OpenSCAD source, preview, and assembly README.
- `renders/` — assembly, plug/socket, anchor, edge-label, exterior-label, size-comparison, and sectional views.

## Validation status

All ten exported STLs are checked for watertightness, consistent winding, one connected body per file, correct nominal radius, successful edge and exterior engraving, A/B clearance, source-spool clearance, radial flange clearance, and axial flange clearance. See `VALIDATION.md` for the generated results from the current files.

Software validation cannot replace a physical fit test. The first print should be one 60° pair because it is the thinnest and therefore the most demanding case.

