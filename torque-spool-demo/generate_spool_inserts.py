"""Parametric plug-together spool inserts for the Spool Paradox demonstrator.

The source meshes were measured in millimetres.  This script intentionally
keeps all user-tunable dimensions in ``PARAMETERS`` and exports one watertight
STL per half for the five requested critical angles.

Coordinate system
-----------------
The insert axis is +Z.  In the assembled spool, translate an insert by
``ASSEMBLY_Z0``.  Half A is the +Y semicylinder and carries the string anchor,
anti-rotation keys, and four plain tapered alignment plugs.  Half B is the -Y
semicylinder and carries complementary push-fit sockets.  There are no hooks
or snap detents; the wound cord supplies retention.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json
import math

import numpy as np
import trimesh
from manifold3d import CrossSection, FillRule, Manifold
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath


OUT_DIR = Path(__file__).resolve().parent


PARAMETERS = {
    # Verified source geometry.
    "rolling_radius": 92.5,          # TPU tire outer surface
    "original_drum_radius": 39.0,    # plastic winding cylinder
    "flange_radius": 90.0,
    "flange_inner_gap": 94.0,        # z=9 to z=103 in assembled coordinates
    # Insert fit.
    "radial_clearance": 0.25,
    "axial_clearance_each_side": 1.5,
    "seam_gap": 0.30,
    "circular_segments": 320,
    # Four tapered push-fit plugs: two axial positions at both seam edges.
    "plug_radial_center": 42.5,
    "plug_base_radius": 2.10,
    "plug_tip_radius": 1.80,
    "plug_length": 5.00,
    "plug_socket_radius": 2.30,
    "plug_socket_depth": 5.35,
    "plug_entry_radius": 2.55,
    "plug_entry_depth": 0.80,
    "plug_axial_stations": (3.5, 87.5),
    # Original anchor: bay x +/-11, z=30.5..50.5, axial post diameter 6.2.
    # The replacement keeps the orientation/location but scales the post only
    # where the 60-degree shell is too thin for the full original depth.
    "anchor_local_z0": 20.0,
    "anchor_height": 20.0,
    "anchor_bay_width": 14.0,
    "anchor_max_depth": 9.0,
    "anchor_back_wall": 1.2,
    "anchor_entry_gap": 0.9,
    "anchor_post_max_radius": 3.1,
    # Keys engage the unused side strips of the original 22 mm anchor bay.
    "key_x_centers": (-9.25, 9.25),
    "key_width": 2.5,
    "key_inward_depth": 2.3,
    "key_local_z0": 24.0,
    "key_height": 12.0,
    # Recessed ID text on the non-winding split faces.
    "engraving_depth": 2.0,
    "label_height": 4.8,
    "label_max_length": 76.0,
    # Large, shallow, two-line ID wrapped around each curved exterior.  The
    # shallow cut keeps the nominal radius on the surrounding cylinder while
    # making the part easy to identify before it is installed.
    "outer_label_depth": 0.80,
    "outer_label_height": 12.0,
    "outer_label_line_gap": 5.0,
    "outer_label_center_z": 63.5,
    "outer_label_angle_span_deg": 150.0,
    "outer_label_refine_length": 1.25,
}


ASSEMBLY_Z0 = 9.0 + PARAMETERS["axial_clearance_each_side"]
INSERT_WIDTH = (
    PARAMETERS["flange_inner_gap"]
    - 2.0 * PARAMETERS["axial_clearance_each_side"]
)
INNER_RADIUS = PARAMETERS["original_drum_radius"] + PARAMETERS["radial_clearance"]
TARGET_ANGLES = (30, 40, 45, 50, 60)


@dataclass
class PartRecord:
    angle_deg: int
    half: str
    target_radius: float
    surface_radius_actual: float
    volume_mm3: float
    vertices: int
    triangles: int
    label: str
    label_removed_volume_mm3: float
    outer_label_removed_volume_mm3: float
    anchor_post_diameter_mm: float | None
    anchor_bay_depth_mm: float | None


def box(size, origin) -> Manifold:
    return Manifold.cube(tuple(float(x) for x in size)).translate(
        tuple(float(x) for x in origin)
    )


def annular_shell(radius: float) -> Manifold:
    seg = int(PARAMETERS["circular_segments"])
    outer = Manifold.cylinder(INSERT_WIDTH, radius, circular_segments=seg)
    inner = Manifold.cylinder(
        INSERT_WIDTH + 2.0, INNER_RADIUS, circular_segments=seg
    ).translate((0, 0, -1.0))
    return outer - inner


def split_half(shell: Manifold, radius: float, half: str) -> Manifold:
    margin = radius + 3.0
    gap = PARAMETERS["seam_gap"]
    if half == "A":
        clip = box(
            (2 * margin, margin, INSERT_WIDTH + 4),
            (-margin, gap / 2, -2),
        )
    else:
        clip = box(
            (2 * margin, margin, INSERT_WIDTH + 4),
            (-margin, -margin - gap / 2, -2),
        )
    return shell ^ clip


def cylinder_along_negative_y(
    length: float,
    radius_base: float,
    radius_tip: float,
    x_center: float,
    z_center: float,
    y_base: float,
) -> Manifold:
    """Create a circular frustum whose axis runs from +Y toward -Y."""
    model = Manifold.cylinder(
        length,
        radius_base,
        radius_tip,
        circular_segments=64,
    )
    matrix = np.array(
        [
            [1, 0, 0, x_center],
            [0, 0, -1, y_base],
            [0, 1, 0, z_center],
        ],
        dtype=float,
    )
    return model.transform(matrix)


def alignment_plugs() -> Manifold:
    """Four plain tapered plugs with no hook, barb, or snap detent."""
    x_abs = PARAMETERS["plug_radial_center"]
    result = Manifold()
    for x_center in (-x_abs, x_abs):
        for z_center in PARAMETERS["plug_axial_stations"]:
            result += cylinder_along_negative_y(
                PARAMETERS["plug_length"],
                PARAMETERS["plug_base_radius"],
                PARAMETERS["plug_tip_radius"],
                x_center,
                z_center,
                0.55,
            )
    return result


def alignment_socket_cutters() -> Manifold:
    """Straight clearance sockets with a short flared lead-in."""
    x_abs = PARAMETERS["plug_radial_center"]
    result = Manifold()
    for x_center in (-x_abs, x_abs):
        for z_center in PARAMETERS["plug_axial_stations"]:
            socket = cylinder_along_negative_y(
                PARAMETERS["plug_socket_depth"],
                PARAMETERS["plug_socket_radius"],
                PARAMETERS["plug_socket_radius"],
                x_center,
                z_center,
                0.35,
            )
            lead_in = cylinder_along_negative_y(
                PARAMETERS["plug_entry_depth"],
                PARAMETERS["plug_entry_radius"],
                PARAMETERS["plug_socket_radius"],
                x_center,
                z_center,
                0.36,
            )
            result += socket + lead_in
    return result


def anti_rotation_keys() -> Manifold:
    """Keys that enter the sides of the existing recessed anchor bay."""
    result = Manifold()
    w = PARAMETERS["key_width"]
    depth = PARAMETERS["key_inward_depth"]
    for xc in PARAMETERS["key_x_centers"]:
        # The y range crosses the measured r=39 surface, creating a robust root.
        result += box(
            (w, depth + 1.1, PARAMETERS["key_height"]),
            (
                xc - w / 2,
                PARAMETERS["original_drum_radius"] - depth,
                PARAMETERS["key_local_z0"],
            ),
        )
    return result


def add_anchor(part: Manifold, radius: float) -> tuple[Manifold, float, float]:
    """Cut a recessed bay and restore an axial capture post.

    The 60-degree shell has only 7 mm nominal radial thickness, so its bay and
    post are proportionally shallower/smaller.  All variants keep a >=1.2 mm
    continuous back wall plus the same 0.9 mm cord-entry slot as the source.
    """
    thickness = radius - INNER_RADIUS
    depth = min(PARAMETERS["anchor_max_depth"],
                thickness - PARAMETERS["anchor_back_wall"])
    if depth <= 3.0:
        raise ValueError("Anchor bay cannot fit in requested shell thickness")
    post_r = min(
        PARAMETERS["anchor_post_max_radius"],
        (depth - 2 * PARAMETERS["anchor_entry_gap"]) / 2,
    )
    z0 = PARAMETERS["anchor_local_z0"]
    height = PARAMETERS["anchor_height"]
    bay = box(
        (PARAMETERS["anchor_bay_width"], depth + 1.0, height),
        (-PARAMETERS["anchor_bay_width"] / 2, radius - depth, z0),
    )
    part = part - bay
    post_y = radius - PARAMETERS["anchor_entry_gap"] - post_r
    post = Manifold.cylinder(
        height + 0.8, post_r, circular_segments=72
    ).translate((0, 0, z0 - 0.4))
    post = post.translate((0, post_y, 0))
    part += post
    return part, depth, 2 * post_r


def label_cross_section(text: str, radius: float) -> CrossSection:
    """Return label contours in (Z, X) coordinates for the +X split face."""
    prop = FontProperties(family="DejaVu Sans", weight="bold")
    paths = TextPath((0, 0), text, size=10.0, prop=prop).to_polygons()
    all_points = np.vstack(paths)
    lo = all_points.min(axis=0)
    hi = all_points.max(axis=0)
    natural = hi - lo
    # Preserve the requested large radial letter height.  If necessary, only
    # condense the text axially to fit the 91 mm-long mating edge.
    x_scale = PARAMETERS["label_height"] / natural[1]
    z_scale = min(x_scale, PARAMETERS["label_max_length"] / natural[0])
    length = natural[0] * z_scale
    x_height = natural[1] * x_scale
    z_start = (INSERT_WIDTH - length) / 2
    x_start = INNER_RADIUS + 0.75 + (PARAMETERS["label_height"] - x_height) / 2
    contours = []
    for polygon in paths:
        p = np.asarray(polygon, dtype=float)
        # TextPath X becomes insert Z; TextPath Y becomes radial X.
        contours.append(
            np.column_stack(
                (
                    (p[:, 0] - lo[0]) * z_scale + z_start,
                    (p[:, 1] - lo[1]) * x_scale + x_start,
                )
            )
        )
    return CrossSection(contours, FillRule.NonZero)


def engraving_cutter(text: str, radius: float, half: str) -> Manifold:
    section = label_cross_section(text, radius)
    depth = PARAMETERS["engraving_depth"] + 0.08
    cutter = section.extrude(depth)
    gap = PARAMETERS["seam_gap"]
    # Extrusion coordinates are (u=Z, v=X, w=depth).  Permute to (X,Y,Z).
    if half == "A":
        matrix = np.array(
            [[0, 1, 0, 0], [0, 0, 1, gap / 2 - 0.04], [1, 0, 0, 0]],
            dtype=float,
        )
    else:
        matrix = np.array(
            [[0, 1, 0, 0], [0, 0, -1, -gap / 2 + 0.04], [1, 0, 0, 0]],
            dtype=float,
        )
    return cutter.transform(matrix)


def outer_label_cross_section(
    text: str,
    radius: float,
    z_start: float,
) -> CrossSection:
    """Return one exterior-label line in unwrapped (arc, Z) coordinates."""
    prop = FontProperties(family="DejaVu Sans", weight="bold")
    paths = TextPath((0, 0), text, size=10.0, prop=prop).to_polygons()
    all_points = np.vstack(paths)
    lo = all_points.min(axis=0)
    hi = all_points.max(axis=0)
    natural = hi - lo
    axial_scale = PARAMETERS["outer_label_height"] / natural[1]
    max_arc = radius * math.radians(PARAMETERS["outer_label_angle_span_deg"])
    arc_scale = min(axial_scale, max_arc / natural[0])
    arc_length = natural[0] * arc_scale
    contours = []
    for polygon in paths:
        p = np.asarray(polygon, dtype=float)
        contours.append(
            np.column_stack(
                (
                    (p[:, 0] - lo[0]) * arc_scale - arc_length / 2,
                    (p[:, 1] - lo[1]) * axial_scale + z_start,
                )
            )
        )
    return CrossSection(contours, FillRule.NonZero)


def outer_engraving_cutter(lines: tuple[str, str], radius: float, half: str) -> Manifold:
    """Create large two-line text following the outside of one semicylinder."""
    line_height = PARAMETERS["outer_label_height"]
    gap = PARAMETERS["outer_label_line_gap"]
    total_height = 2 * line_height + gap
    z0 = PARAMETERS["outer_label_center_z"] - total_height / 2
    center_angle = math.pi / 2 if half == "A" else -math.pi / 2
    result = Manifold()
    for index, line in enumerate(lines):
        section = outer_label_cross_section(
            line,
            radius,
            z0 + (1 - index) * (line_height + gap),
        )
        # Refine the planar text before bending it so straight glyph edges
        # follow the cylinder instead of becoming long chords.
        flat = section.extrude(PARAMETERS["outer_label_depth"] + 0.12)
        flat = flat.refine_to_length(PARAMETERS["outer_label_refine_length"])

        def wrap(vertices):
            vertices = np.asarray(vertices, dtype=float)
            arc = vertices[:, 0]
            axial = vertices[:, 1]
            inward = vertices[:, 2]
            # Reverse arc direction so the text reads normally when viewed
            # radially from outside either semicylinder.
            theta = center_angle - arc / radius
            radial = radius + 0.06 - inward
            return np.column_stack(
                (radial * np.cos(theta), radial * np.sin(theta), axial)
            )

        result += flat.warp_batch(wrap)
    return result


def make_pair(angle: int) -> tuple[Manifold, Manifold, dict]:
    radius = PARAMETERS["rolling_radius"] * math.cos(math.radians(angle))
    if radius <= INNER_RADIUS:
        raise ValueError(f"{angle} degrees produces no viable shell")
    base = annular_shell(radius)
    a = split_half(base, radius, "A")
    b = split_half(base, radius, "B")

    a += alignment_plugs() + anti_rotation_keys()
    b -= alignment_socket_cutters()
    a, anchor_depth, anchor_post_diameter = add_anchor(a, radius)

    label = f"{angle}\N{DEGREE SIGN} FROM HORIZONTAL | r={radius:.1f} mm"
    outer_label_lines = (
        f"{angle}\N{DEGREE SIGN} FROM HORIZONTAL",
        f"r = {radius:.1f} mm",
    )
    outer_cut_a = outer_engraving_cutter(outer_label_lines, radius, "A")
    outer_cut_b = outer_engraving_cutter(outer_label_lines, radius, "B")
    outer_a_before = a.volume()
    outer_b_before = b.volume()
    a -= outer_cut_a
    b -= outer_cut_b
    outer_a_removed = max(0.0, outer_a_before - a.volume())
    outer_b_removed = max(0.0, outer_b_before - b.volume())

    cut_a = engraving_cutter(label, radius, "A")
    cut_b = engraving_cutter(label, radius, "B")
    a_before = a.volume()
    b_before = b.volume()
    a -= cut_a
    b -= cut_b

    overlap = (a ^ b).volume()
    meta = {
        "angle_deg": angle,
        "target_radius_mm": radius,
        "nominal_shell_thickness_mm": radius - INNER_RADIUS,
        "label": label,
        "outer_label_lines": outer_label_lines,
        "anchor_depth_mm": anchor_depth,
        "anchor_post_diameter_mm": anchor_post_diameter,
        "label_removed_volume_A_mm3": max(0.0, a_before - a.volume()),
        "label_removed_volume_B_mm3": max(0.0, b_before - b.volume()),
        "outer_label_removed_volume_A_mm3": outer_a_removed,
        "outer_label_removed_volume_B_mm3": outer_b_removed,
        "assembled_overlap_mm3": overlap,
    }
    return a, b, meta


def export_manifold(model: Manifold, path: Path) -> trimesh.Trimesh:
    if model.is_empty() or str(model.status()) != "Error.NoError":
        raise RuntimeError(f"Invalid manifold before export: {model.status()}")
    mesh = model.to_mesh()
    vertices = np.asarray(mesh.vert_properties, dtype=float)[:, :3]
    faces = np.asarray(mesh.tri_verts, dtype=np.int64)
    tri = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    tri.export(path)
    return tri


def generate() -> None:
    records: list[PartRecord] = []
    designs = {}
    for angle in TARGET_ANGLES:
        a, b, meta = make_pair(angle)
        designs[str(angle)] = meta
        for half, model in (("A", a), ("B", b)):
            path = OUT_DIR / f"Spool_Insert_{angle}deg_{half}.stl"
            tri = export_manifold(model, path)
            radial = np.linalg.norm(tri.vertices[:, :2], axis=1)
            records.append(
                PartRecord(
                    angle_deg=angle,
                    half=half,
                    target_radius=meta["target_radius_mm"],
                    surface_radius_actual=float(radial.max()),
                    volume_mm3=float(abs(tri.volume)),
                    vertices=len(tri.vertices),
                    triangles=len(tri.faces),
                    label=meta["label"],
                    label_removed_volume_mm3=meta[
                        f"label_removed_volume_{half}_mm3"
                    ],
                    outer_label_removed_volume_mm3=meta[
                        f"outer_label_removed_volume_{half}_mm3"
                    ],
                    anchor_post_diameter_mm=(
                        meta["anchor_post_diameter_mm"] if half == "A" else None
                    ),
                    anchor_bay_depth_mm=(
                        meta["anchor_depth_mm"] if half == "A" else None
                    ),
                )
            )
            print(
                f"wrote {path.name}: {len(tri.vertices)} vertices, "
                f"{len(tri.faces)} triangles"
            )

    manifest = {
        "units": "mm",
        "parameters": PARAMETERS,
        "assembly_z0_mm": ASSEMBLY_Z0,
        "insert_width_mm": INSERT_WIDTH,
        "inner_radius_mm": INNER_RADIUS,
        "designs": designs,
        "parts": [asdict(record) for record in records],
    }
    (OUT_DIR / "design_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    generate()
