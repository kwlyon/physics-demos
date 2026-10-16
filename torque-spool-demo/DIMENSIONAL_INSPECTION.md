# Dimensional inspection of supplied spool files

All three source STLs were loaded, vertex-welded, checked as closed meshes, and measured in millimetres before the insert geometry was created. The originals were read only and remain in their supplied location.

## Verified dimensions

| Feature | Measured value |
|---|---:|
| TPU tire outside diameter | 185.000 mm |
| TPU tire inside diameter | 176.000 mm |
| TPU tire axial width | 8.000 mm |
| Plastic flange outside diameter | 180.000 mm |
| Original winding-cylinder diameter | 78.000 mm |
| Original winding-cylinder radius | 39.000 mm |
| Assembled outside-face spacing | 112.000 mm |
| Inner flange faces | z = 9.000 and 103.000 mm |
| Clear axial width between flange faces | 94.000 mm |
| Central through-bore diameter | 36.000 mm |

The male half has a nominal 29.0 mm-radius plug from local z=56 to 69 mm. The female half has a mating socket with an approximately 29.38 mm inner radius from local z=42.7 to 56 mm. With the female part inverted, the connector regions meet at an assembled outside-face spacing of approximately 112 mm. The exposed winding surface is a continuous 39 mm-radius cylinder from the male flange to the female flange.

The TPU tire has an 88 mm inner radius and fits the 90 mm plastic rim as an interference/stretch fit. Its 92.5 mm outer radius is therefore the rolling radius used in the physics calculation.

## Original string anchor

The anchor is on the +Y side of the male winding cylinder. It is not a simple hole. Exact mesh sections show:

- A recessed bay 22.0 mm wide in X.
- An axial span from male-local z=30.5 to 50.5 mm.
- A radial floor at y=29.0 mm behind the 39.0 mm winding surface.
- A captive axial post centered at x=0, y=35.0 mm.
- Post diameter 6.2 mm.
- Approximately 0.9 mm between the post and the outer lip, with a larger capture space behind it.

The insert anchor uses the same angular location, axial location, recessed-bay arrangement, and axial post orientation. The 30°, 40°, and 50° inserts retain a 6.2 mm post. The 60° shell is only 7.0 mm thick, so its bay is 5.8 mm deep and its post is reduced to 4.0 mm diameter while retaining the 0.9 mm entry slot and a 1.2 mm back wall.

## Interference and access assessment

- Flange spokes, the central through-bore, and the male/female connector are radially inside the 39 mm winding surface and do not obstruct the shells.
- The insert occupies 91.0 of the available 94.0 mm, leaving 1.5 mm clearance at each flange.
- The largest insert radius is 80.107 mm, leaving 9.893 mm to the 90 mm plastic flange radius and 12.393 mm to the TPU rolling surface.
- The shells mount radially from opposite sides; the spool does not need to be disassembled.
- Two inner keys on half A enter unused side regions of the original anchor bay. They prevent meaningful rotation and axial sliding without colliding with the original 6.2 mm post.

## Source identification

SHA-256 hashes recorded after inspection:

```text
4BC72B991C64DE3614C0735976C5241D6FAC0A9BF063C050420E728D1E4D21BE  Optional_TPU_tire_print_2x.stl
B9F297FF77B743029FF91B233FCA5523EE1F22C58F4AF685B033B0B4FBDB45B9  Spool_FEMALE_print_1x.stl
474F3E7E619FD8DC2648FAEB55DDB1C07095481D863995916B90818F822E970E  Spool_MALE_print_1x.stl
```

