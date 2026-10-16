"""Generate hollow, screw-together sleeve caps for the spool's center bore.

The supplied male and female spool halves assemble to 112.0 mm between their
outside wheel faces and share a nominal 36.0 mm through-bore. This generator
exports one STL containing a male cap and a female cap. Thin annular sleeves
follow the bore wall and thread together near the middle, leaving the axial
core available for lead shot while clamping both end flanges against the spool.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import numpy as np
import trimesh
from manifold3d import CrossSection, FillRule, Manifold


ROOT = Path(__file__).resolve().parent
OUTPUT_STL = ROOT / "Axle_Bore_Clamp_Plugs_print_1set.stl"
VALIDATION_JSON = ROOT / "axle_bore_clamp_plug_validation.json"
RENDER_PATH = ROOT / "renders" / "axle_bore_clamp_plugs.png"


@dataclass(frozen=True)
class ClampPlugSpec:
    bore_diameter_mm: float = 36.0
    assembled_outside_face_spacing_mm: float = 112.0
    sleeve_outer_diameter_mm: float = 35.4
    sleeve_main_inner_diameter_mm: float = 30.0
    flange_diameter_mm: float = 44.0
    flange_thickness_mm: float = 5.0
    sealed_end_wall_mm: float = 3.0
    flange_sides: int = 12
    sleeve_reach_from_flange_mm: float = 66.0
    male_thread_tube_inner_diameter_mm: float = 23.8
    male_thread_root_diameter_mm: float = 27.8
    thread_pitch_mm: float = 3.5
    male_thread_major_diameter_mm: float = 30.0
    female_thread_minor_diameter_mm: float = 28.8
    female_thread_major_diameter_mm: float = 31.6
    male_shoulder_start_from_outer_face_mm: float = 48.0
    thread_start_from_outer_face_mm: float = 49.5
    thread_end_from_outer_face_mm: float = 69.5
    pair_center_spacing_mm: float = 58.0
    circular_segments: int = 128
    thread_divisions_per_turn: int = 90


SPEC = ClampPlugSpec()


def cylinder(
    height: float,
    radius_low: float,
    radius_high: float,
    z: float,
    segments: int | None = None,
) -> Manifold:
    return Manifold.cylinder(
        height,
        radius_low,
        radius_high,
        circular_segments=segments or SPEC.circular_segments,
    ).translate((0, 0, z))


def polar(radius: float, angle_deg: float) -> tuple[float, float]:
    angle = math.radians(angle_deg)
    return radius * math.cos(angle), radius * math.sin(angle)


def helical_ridge(
    z0: float,
    length: float,
    root_radius: float,
    crest_radius: float,
    pitch: float,
    root_half_angle_deg: float,
    crest_half_angle_deg: float,
    twist_direction: float = 1.0,
) -> Manifold:
    """Create one continuous coarse helical ridge around the Z axis."""
    points = [
        polar(root_radius, -root_half_angle_deg),
        polar(crest_radius, -crest_half_angle_deg),
        polar(crest_radius, crest_half_angle_deg),
        polar(root_radius, root_half_angle_deg),
    ]
    section = CrossSection([points], FillRule.NonZero)
    turns = length / pitch
    divisions = max(8, math.ceil(turns * SPEC.thread_divisions_per_turn))
    return section.extrude(
        length,
        n_divisions=divisions,
        twist_degrees=twist_direction * 360.0 * turns,
    ).translate((0, 0, z0))


def common_flange() -> Manifold:
    flange_r = SPEC.flange_diameter_mm / 2
    fh = SPEC.flange_thickness_mm
    return cylinder(
        fh,
        flange_r,
        flange_r - 0.4,
        0,
        segments=SPEC.flange_sides,
    )


def make_male_cap() -> Manifold:
    fh = SPEC.flange_thickness_mm
    tip_z = fh + SPEC.sleeve_reach_from_flange_mm
    sleeve_outer_r = SPEC.sleeve_outer_diameter_mm / 2
    sleeve_inner_r = SPEC.sleeve_main_inner_diameter_mm / 2
    tube_inner_r = SPEC.male_thread_tube_inner_diameter_mm / 2
    root_r = SPEC.male_thread_root_diameter_mm / 2
    major_r = SPEC.male_thread_major_diameter_mm / 2
    shoulder_z0 = SPEC.male_shoulder_start_from_outer_face_mm
    thread_z0 = SPEC.thread_start_from_outer_face_mm
    thread_z1 = SPEC.thread_end_from_outer_face_mm

    body = common_flange()
    body += cylinder(shoulder_z0 - fh, sleeve_outer_r, sleeve_outer_r, fh)
    body += cylinder(
        thread_z0 - shoulder_z0,
        sleeve_outer_r,
        root_r,
        shoulder_z0,
    )
    body += cylinder(tip_z - thread_z0 - 1.5, root_r, root_r, thread_z0)
    body += cylinder(1.5, root_r, root_r - 0.8, tip_z - 1.5)
    body += helical_ridge(
        thread_z0,
        thread_z1 - thread_z0,
        root_r,
        major_r,
        SPEC.thread_pitch_mm,
        root_half_angle_deg=66.0,
        crest_half_angle_deg=22.0,
    )

    # Open the cup all the way to its inward-facing tip. The exposed flange
    # retains a 3 mm sealing wall; only the short threaded end necks down.
    cavity = cylinder(
        shoulder_z0 - SPEC.sealed_end_wall_mm,
        sleeve_inner_r,
        sleeve_inner_r,
        SPEC.sealed_end_wall_mm,
    )
    cavity += cylinder(
        thread_z0 - shoulder_z0,
        sleeve_inner_r,
        tube_inner_r,
        shoulder_z0,
    )
    cavity += cylinder(
        tip_z - thread_z0 + 0.2,
        tube_inner_r,
        tube_inner_r,
        thread_z0,
    )
    body -= cavity
    return body


def make_female_cap() -> Manifold:
    fh = SPEC.flange_thickness_mm
    tip_z = fh + SPEC.sleeve_reach_from_flange_mm
    outer_r = SPEC.sleeve_outer_diameter_mm / 2
    main_inner_r = SPEC.sleeve_main_inner_diameter_mm / 2
    minor_r = SPEC.female_thread_minor_diameter_mm / 2
    major_r = SPEC.female_thread_major_diameter_mm / 2
    thread_z0 = SPEC.thread_start_from_outer_face_mm
    thread_z1 = SPEC.thread_end_from_outer_face_mm

    body = common_flange()
    body += cylinder(tip_z - fh, outer_r, outer_r, fh)
    mirror_z = SPEC.assembled_outside_face_spacing_mm + 2 * fh
    groove_local_z0 = mirror_z - thread_z1
    bore_z0 = groove_local_z0 - 1.0
    main_cavity = cylinder(
        bore_z0 - SPEC.sealed_end_wall_mm + 0.1,
        main_inner_r,
        main_inner_r,
        SPEC.sealed_end_wall_mm,
    )
    bore = cylinder(tip_z - bore_z0 + 0.2, minor_r, minor_r, bore_z0)
    # Build the receiver groove in the male cap's coordinate system, then
    # map it into the opposing cap. At the seated design phase, the STL
    # facets align exactly instead of merely approximating the same helix.
    groove = helical_ridge(
        thread_z0,
        thread_z1 - thread_z0,
        minor_r,
        major_r,
        SPEC.thread_pitch_mm,
        root_half_angle_deg=76.0,
        crest_half_angle_deg=26.0,
    )
    groove_map = np.array(
        [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, -1.0, 0.0, 0.0],
            [0.0, 0.0, -1.0, mirror_z],
        ],
        dtype=float,
    )
    groove = groove.transform(groove_map)
    entry = cylinder(
        1.7,
        minor_r,
        major_r + 0.45,
        tip_z - 1.5,
    )
    body -= main_cavity + bore + groove + entry
    return body


def export_manifold(model: Manifold, path: Path) -> trimesh.Trimesh:
    if model.is_empty() or str(model.status()) != "Error.NoError":
        raise RuntimeError(f"Invalid manifold before export: {model.status()}")
    mesh = model.to_mesh()
    vertices = np.asarray(mesh.vert_properties, dtype=float)[:, :3]
    faces = np.asarray(mesh.tri_verts, dtype=np.int64)
    tri = trimesh.Trimesh(
        vertices=vertices,
        faces=faces,
        process=True,
        validate=True,
    )

    # Manifold's threaded boolean can leave coincident two-triangle slivers
    # that have zero volume but become detached components after STL's float32
    # round trip. Remove them here so slicers see exactly the two cap bodies.
    printable = [
        component
        for component in tri.split(only_watertight=False, repair=False)
        if len(component.faces) > 4 and abs(float(component.volume)) > 0.01
    ]
    if len(printable) != 2:
        raise RuntimeError(
            f"Expected two printable cap bodies; found {len(printable)}"
        )
    tri = trimesh.util.concatenate(printable)
    tri.export(path)

    # Validate what was actually serialized, rather than only the source mesh.
    roundtrip = trimesh.load(path, force="mesh", process=True)
    roundtrip_parts = [
        component
        for component in roundtrip.split(only_watertight=False, repair=False)
        if len(component.faces) > 4 and abs(float(component.volume)) > 0.01
    ]
    if len(roundtrip_parts) != 2:
        raise RuntimeError(
            f"STL round trip produced {len(roundtrip_parts)} printable bodies"
        )
    if len(roundtrip.split(only_watertight=False, repair=False)) != 2:
        roundtrip = trimesh.util.concatenate(roundtrip_parts)
        roundtrip.export(path)
        roundtrip = trimesh.load(path, force="mesh", process=True)
    return roundtrip


def seated_female_transform(
    rotation_deg: float,
    outward_offset_mm: float = 0.0,
) -> np.ndarray:
    angle = math.radians(rotation_deg)
    c, s = math.cos(angle), math.sin(angle)
    rz = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=float)
    flip = np.diag([1.0, -1.0, -1.0])
    matrix = np.zeros((3, 4), dtype=float)
    matrix[:3, :3] = rz @ flip
    matrix[2, 3] = (
        SPEC.assembled_outside_face_spacing_mm + SPEC.flange_thickness_mm
        + outward_offset_mm
    )
    return matrix


def validate_seated_fit(
    male: Manifold,
    female: Manifold,
) -> tuple[float, float]:
    """Search thread phase and report the smallest seated overlap volume."""
    male_seated = male.translate((0, 0, -SPEC.flange_thickness_mm))
    best_phase = 0.0
    best_overlap = float("inf")
    for phase in np.arange(0.0, 360.0, 10.0):
        female_seated = female.transform(seated_female_transform(float(phase)))
        overlap = max(0.0, float((male_seated ^ female_seated).volume()))
        if overlap < best_overlap:
            best_phase = float(phase)
            best_overlap = overlap
    for phase in np.arange(best_phase - 10.0, best_phase + 10.1, 1.0):
        female_seated = female.transform(seated_female_transform(float(phase)))
        overlap = max(0.0, float((male_seated ^ female_seated).volume()))
        if overlap < best_overlap:
            best_phase = float(phase % 360.0)
            best_overlap = overlap
    return best_phase, best_overlap


def thread_engagement_when_seated() -> float:
    male_start = (
        SPEC.thread_start_from_outer_face_mm - SPEC.flange_thickness_mm
    )
    male_end = SPEC.thread_end_from_outer_face_mm - SPEC.flange_thickness_mm
    female_start = (
        SPEC.assembled_outside_face_spacing_mm
        - SPEC.sleeve_reach_from_flange_mm
    )
    female_end = male_end
    return max(0.0, min(male_end, female_end) - max(male_start, female_start))


def validate_thread_path(
    male: Manifold,
    female: Manifold,
    seated_phase_deg: float,
) -> float:
    """Check clearance while the female cap follows the helical removal path."""
    male_seated = male.translate((0, 0, -SPEC.flange_thickness_mm))
    engagement = thread_engagement_when_seated()
    offsets = np.arange(0.0, engagement + SPEC.thread_pitch_mm + 0.01, 0.5)
    maximum_overlap = 0.0
    for offset in offsets:
        phase = (
            seated_phase_deg
            + 360.0 * float(offset) / SPEC.thread_pitch_mm
        )
        female_moving = female.transform(
            seated_female_transform(phase, float(offset))
        )
        maximum_overlap = max(
            maximum_overlap,
            max(0.0, float((male_seated ^ female_moving).volume())),
        )
    return maximum_overlap


def render_design() -> None:
    S = SPEC
    flange_r = S.flange_diameter_mm / 2
    sleeve_outer_r = S.sleeve_outer_diameter_mm / 2
    sleeve_inner_r = S.sleeve_main_inner_diameter_mm / 2
    thread_root_r = S.male_thread_root_diameter_mm / 2
    thread_inner_r = S.male_thread_tube_inner_diameter_mm / 2
    fh = S.flange_thickness_mm
    shoulder_z = S.male_shoulder_start_from_outer_face_mm
    thread_z = S.thread_start_from_outer_face_mm
    tip_z = fh + S.sleeve_reach_from_flange_mm

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=180)
    male_outline = [
        (0, -flange_r), (fh, -flange_r + 0.4),
        (fh, -sleeve_outer_r), (shoulder_z, -sleeve_outer_r),
        (thread_z, -thread_root_r), (tip_z, -thread_root_r + 0.8),
        (tip_z, thread_root_r - 0.8), (thread_z, thread_root_r),
        (shoulder_z, sleeve_outer_r), (fh, sleeve_outer_r),
        (fh, flange_r - 0.4), (0, flange_r),
    ]
    ax1.add_patch(Polygon(male_outline, closed=True, facecolor="#dcecf5",
                          edgecolor="#163a5f", linewidth=1.4))
    male_cavity = [
        (S.sealed_end_wall_mm, -sleeve_inner_r),
        (shoulder_z, -sleeve_inner_r),
        (thread_z, -thread_inner_r),
        (tip_z + 0.2, -thread_inner_r),
        (tip_z + 0.2, thread_inner_r),
        (thread_z, thread_inner_r),
        (shoulder_z, sleeve_inner_r),
        (S.sealed_end_wall_mm, sleeve_inner_r),
    ]
    ax1.add_patch(Polygon(male_cavity, closed=True, facecolor="#fff7dc",
                          edgecolor="#9a6700", linewidth=1.1))
    ax1.axhline(S.bore_diameter_mm / 2, color="#d97706", ls="--", lw=1.1)
    ax1.axhline(-S.bore_diameter_mm / 2, color="#d97706", ls="--", lw=1.1)
    ax1.axvspan(S.thread_start_from_outer_face_mm,
                S.thread_end_from_outer_face_mm,
                color="#2474a6", alpha=0.18, label="coarse male thread")
    ax1.set_aspect("equal", adjustable="box")
    ax1.set_title("Hollow male sleeve cross-section")
    ax1.set_xlabel("distance from exposed cap face (mm)")
    ax1.set_ylabel("radius (mm)")
    ax1.grid(alpha=0.18)
    ax1.legend(loc="upper right")

    right_face = S.assembled_outside_face_spacing_mm
    male_tip = S.sleeve_reach_from_flange_mm
    female_tip = right_face - S.sleeve_reach_from_flange_mm
    ax2.add_patch(plt.Rectangle(
        (0, -S.bore_diameter_mm / 2),
        right_face,
        S.bore_diameter_mm,
        facecolor="#f3f5f7", edgecolor="#38434f", lw=1.2,
    ))
    ax2.add_patch(plt.Rectangle(
        (0, -thread_inner_r), right_face, 2 * thread_inner_r,
        facecolor="#f6c453", edgecolor="none", alpha=0.42,
        label="minimum continuous shot space",
    ))
    male_main_end = shoulder_z - fh
    male_thread_start = thread_z - fh
    female_thread_end = right_face + fh - S.thread_start_from_outer_face_mm
    ax2.plot([0, male_main_end], [sleeve_outer_r, sleeve_outer_r],
             color="#2474a6", lw=3, label="male hollow sleeve")
    ax2.plot([0, male_main_end], [-sleeve_outer_r, -sleeve_outer_r],
             color="#2474a6", lw=3)
    ax2.plot([0, male_main_end], [sleeve_inner_r, sleeve_inner_r],
             color="#2474a6", lw=1.3)
    ax2.plot([0, male_main_end], [-sleeve_inner_r, -sleeve_inner_r],
             color="#2474a6", lw=1.3)
    ax2.plot([male_thread_start, male_tip], [thread_root_r, thread_root_r],
             color="#2474a6", lw=3)
    ax2.plot([male_thread_start, male_tip], [-thread_root_r, -thread_root_r],
             color="#2474a6", lw=3)
    ax2.plot([male_thread_start, male_tip], [thread_inner_r, thread_inner_r],
             color="#2474a6", lw=1.3)
    ax2.plot([male_thread_start, male_tip], [-thread_inner_r, -thread_inner_r],
             color="#2474a6", lw=1.3)

    ax2.plot([female_tip, right_face], [sleeve_outer_r, sleeve_outer_r],
             color="#d97706", lw=3, label="female hollow sleeve")
    ax2.plot([female_tip, right_face], [-sleeve_outer_r, -sleeve_outer_r],
             color="#d97706", lw=3)
    ax2.plot([female_thread_end, right_face], [sleeve_inner_r, sleeve_inner_r],
             color="#d97706", lw=1.3)
    ax2.plot([female_thread_end, right_face], [-sleeve_inner_r, -sleeve_inner_r],
             color="#d97706", lw=1.3)
    female_minor_r = S.female_thread_minor_diameter_mm / 2
    ax2.plot([female_tip, female_thread_end], [female_minor_r, female_minor_r],
             color="#d97706", lw=1.3)
    ax2.plot([female_tip, female_thread_end], [-female_minor_r, -female_minor_r],
             color="#d97706", lw=1.3)
    ax2.axvline(0, color="#163a5f", lw=5)
    ax2.axvline(right_face, color="#163a5f", lw=5)
    ax2.annotate(
        f"{thread_engagement_when_seated():.1f} mm threaded overlap",
        xy=((male_tip + female_tip) / 2, 0),
        xytext=((male_tip + female_tip) / 2, 11),
        ha="center",
        arrowprops={"arrowstyle": "->", "color": "#38434f"},
    )
    ax2.set_xlim(-8, 120)
    ax2.set_ylim(-22, 22)
    ax2.set_aspect("equal", adjustable="box")
    ax2.set_title("Hollow sleeves seated in the 112 mm bore")
    ax2.set_xlabel("assembled axial position (mm)")
    ax2.set_yticks([])
    ax2.legend(loc="lower center", ncol=2)

    fig.suptitle(
        "Hollow Screw-Together Axle-Bore Sleeve Caps",
        color="#163a5f",
        fontsize=15,
        fontweight="bold",
    )
    fig.tight_layout()
    RENDER_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(RENDER_PATH, bbox_inches="tight")
    plt.close(fig)


def generate() -> None:
    male = make_male_cap()
    female = make_female_cap()
    phase_deg, seated_overlap_mm3 = validate_seated_fit(male, female)
    thread_path_overlap_mm3 = validate_thread_path(male, female, phase_deg)

    half_spacing = SPEC.pair_center_spacing_mm / 2
    print_set = male.translate((-half_spacing, 0, 0))
    print_set += female.translate((half_spacing, 0, 0))
    tri = export_manifold(print_set, OUTPUT_STL)
    components = tri.split(only_watertight=False, repair=False)

    sleeve_overlap = (
        2 * SPEC.sleeve_reach_from_flange_mm
        - SPEC.assembled_outside_face_spacing_mm
    )
    male_seated = male.translate((0, 0, -SPEC.flange_thickness_mm))
    female_seated = female.transform(seated_female_transform(phase_deg))
    bore = cylinder(
        SPEC.assembled_outside_face_spacing_mm,
        SPEC.bore_diameter_mm / 2,
        SPEC.bore_diameter_mm / 2,
        0,
    )
    bore_volume_mm3 = float(bore.volume())
    plug_material_in_bore_mm3 = float(((male_seated + female_seated) ^ bore).volume())
    available_bore_void_mm3 = bore_volume_mm3 - plug_material_in_bore_mm3
    report = {
        "units": "mm",
        "source_dimensions": {
            "bore_diameter_mm": 36.0,
            "assembled_outside_face_spacing_mm": 112.0,
        },
        "specification": asdict(SPEC),
        "output_file": OUTPUT_STL.name,
        "vertices": int(len(tri.vertices)),
        "triangles": int(len(tri.faces)),
        "body_count": int(len(components)),
        "watertight": bool(tri.is_watertight),
        "winding_consistent": bool(tri.is_winding_consistent),
        "mesh_extents_mm": tri.extents.tolist(),
        "volume_set_mm3": float(abs(tri.volume)),
        "sleeve_radial_clearance_mm": (
            SPEC.bore_diameter_mm - SPEC.sleeve_outer_diameter_mm
        ) / 2,
        "sleeve_overlap_when_seated_mm": sleeve_overlap,
        "thread_engagement_when_seated_mm": thread_engagement_when_seated(),
        "minimum_continuous_shot_diameter_mm": (
            SPEC.male_thread_tube_inner_diameter_mm
        ),
        "available_bore_void_mm3": available_bore_void_mm3,
        "available_bore_void_percent": (
            100.0 * available_bore_void_mm3 / bore_volume_mm3
        ),
        "best_seated_thread_phase_deg": phase_deg,
        "best_seated_mesh_overlap_mm3": seated_overlap_mm3,
        "max_thread_path_mesh_overlap_mm3": thread_path_overlap_mm3,
        "thread_path_clearance_check_passed": thread_path_overlap_mm3 < 0.1,
    }
    VALIDATION_JSON.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )
    render_design()

    print(
        f"wrote {OUTPUT_STL.name}: {len(tri.vertices)} vertices, "
        f"{len(tri.faces)} triangles, {len(components)} bodies"
    )
    print(
        f"seated sleeves overlap {sleeve_overlap:.1f} mm; "
        f"best thread phase {phase_deg:.1f} degrees; "
        f"mesh overlap {seated_overlap_mm3:.4f} mm^3; "
        f"thread-path maximum {thread_path_overlap_mm3:.4f} mm^3; "
        f"available bore void {available_bore_void_mm3:.0f} mm^3"
    )


if __name__ == "__main__":
    generate()
