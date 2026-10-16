# Geometric validation report

Overall result: **PASS**

All dimensions are millimetres. Checks were repeated on the exported STL files, not only on the in-memory CAD solids.

## Per-file checks

| File | Watertight | One body | Radius error | Spool overlap | Min spool gap | Edge label cut | Outer label cut |
|---|---:|---:|---:|---:|---:|---:|---:|
| Spool_Insert_30deg_A.stl | True | True | +0.000004 | 0.000000 mm³ | 0.2499 | 231.60 mm³ | 1315.55 mm³ |
| Spool_Insert_30deg_B.stl | True | True | +0.000004 | 0.000000 mm³ | 0.2499 | 231.60 mm³ | 1315.55 mm³ |
| Spool_Insert_40deg_A.stl | True | True | +0.000004 | 0.000000 mm³ | 0.2499 | 230.58 mm³ | 1218.13 mm³ |
| Spool_Insert_40deg_B.stl | True | True | +0.000004 | 0.000000 mm³ | 0.2499 | 230.58 mm³ | 1218.13 mm³ |
| Spool_Insert_45deg_A.stl | True | True | +0.000004 | 0.000000 mm³ | 0.2499 | 230.65 mm³ | 1154.34 mm³ |
| Spool_Insert_45deg_B.stl | True | True | +0.000004 | 0.000000 mm³ | 0.2499 | 230.65 mm³ | 1154.34 mm³ |
| Spool_Insert_50deg_A.stl | True | True | +0.000002 | 0.000000 mm³ | 0.2499 | 232.27 mm³ | 1090.05 mm³ |
| Spool_Insert_50deg_B.stl | True | True | +0.000002 | 0.000000 mm³ | 0.2499 | 232.27 mm³ | 1090.05 mm³ |
| Spool_Insert_60deg_A.stl | True | True | +0.000002 | 0.000000 mm³ | 0.2499 | 232.31 mm³ | 926.05 mm³ |
| Spool_Insert_60deg_B.stl | True | True | +0.000002 | 0.000000 mm³ | 0.2499 | 232.31 mm³ | 926.05 mm³ |

## Pair and clearance checks

| Angle | Radius | Nominal shell | A/B overlap | Plug clearance | Flange clearance | Axial clearance/side |
|---:|---:|---:|---:|---:|---:|---:|
| 30° | 80.107 | 40.857 | 0.000000 mm³ | 0.2586 | 9.893 | 1.500 |
| 40° | 70.859 | 31.609 | 0.000000 mm³ | 0.2586 | 19.141 | 1.500 |
| 45° | 65.407 | 26.157 | 0.000000 mm³ | 0.2586 | 24.593 | 1.500 |
| 50° | 59.458 | 20.208 | 0.000000 mm³ | 0.2586 | 30.542 | 1.500 |
| 60° | 46.250 | 7.000 | 0.000000 mm³ | 0.2586 | 43.750 | 1.500 |

## Limits of validation

- No physical test print or push-fit trial was possible in software.
- Cord diameter was not supplied. Radius labels denote the actual cylindrical winding surface; add half the cord diameter for a first-layer centerline radius.
- A slicer-specific overhang/bridging simulation was not performed. The four short horizontal alignment plugs are the only features likely to benefit from local support.
