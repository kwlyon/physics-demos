"""Generate rigid, screw-together end caps for the spool's center bore.

The supplied male and female spool halves assemble to 112.0 mm between their
outside wheel faces and share a nominal 36.0 mm through-bore. This generator
exports one STL containing a male cap and a female cap. Long central stems
meet inside the bore and use a coarse printed thread to clamp both end flanges
against the spool, making retention independent of friction.
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
    guide_shank_diameter_mm: float = 35.4
    guide_shank_length_mm: float = 14.0
    guide_tip_diameter_mm: float = 34.0
    flange_diameter_mm: float = 44.0
    flange_thickness_mm: float = 5.0
    flange_sides: int = 12
    stem_length_from_flange_mm: float = 66.0
    male_stem_root_diameter_mm: float = 10.8
    female_stem_outer_diameter_mm: float = 21.0
    thread_pitch_mm: float = 3.5
    male_thread_major_diameter_mm: float = 13.0
    female_thread_minor_diameter_mm: float = 12.4
    female_thread_major_diameter_mm: float = 14.8
    thread_start_from_outer_face_mm: float = 48.5
    thread_end_from_outer_face_mm: float = 69.5
    pair_center_spacing_mm: float = 58.0
    circular_segments: int = 128
    thread_divisions_per_turn: int = 30


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
        twist_degrees=360.0 * turns,
    ).translate((0, 0, z0))


def common_cap_and_guide() -> Manifold:
    flange_r = SPEC.flange_diameter_mm / 2
    shank_r = SPEC.guide_shank_diameter_mm / 2
    tip_r = SPEC.guide_tip_diameter_mm / 2
    fh = SPEC.flange_thickness_mm
    shank_end = fh + SPEC.guide_shank_length_mm

    cap = cylinder(
        fh,
        flange_r,
        flange_r - 0.4,
        0,
        segments=SPEC.flange_sides,
    )
    cap += cylinder(
        SPEC.guide_shank_length_mm - 1.8,
        shank_r,
        shank_r,
        fh,
    )
    cap += cylinder(
        1.8,
        shank_r,
        tip_r,
        shank_end - 1.8,
    )
    cap += cylinder(1.8, flange_r - 2.2, shank_r, fh - 0.5)
    return cap


def make_male_cap() -> Manifold:
    fh = SPEC.flange_thickness_mm
    tip_z = fh + SPEC.stem_length_from_flange_mm
    root_r = SPEC.male_stem_root_diameter_mm / 2
    major_r = SPEC.male_thread_major_diameter_mm / 2
    thread_z0 = SPEC.thread_start_from_outer_face_mm
    thread_z1 = SPEC.thread_end_from_outer_face_mm

    body = common_cap_and_guide()
    body += cylinder(tip_z - fh - 1.5, root_r, root_r, fh)
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
    return body


def make_female_cap() -> Manifold:
    fh = SPEC.flange_thickness_mm
    tip_z = fh + SPEC.stem_length_from_flange_mm
    outer_r = SPEC.female_stem_outer_diameter_mm / 2
    minor_r = SPEC.female_thread_minor_diameter_mm / 2
    major_r = SPEC.female_thread_major_diameter_mm / 2
    thread_z0 = SPEC.thread_start_from_outer_face_mm
    thread_z1 = SPEC.thread_end_from_outer_face_mm

    body = common_cap_and_guide()
    body += cylinder(tip_z - fh, outer_r, outer_r, fh)
    bore_z0 = thread_z0 - 1.0
    bore = cylinder(tip_z - bore_z0 + 0.2, minor_r, minor_r, bore_z0)
    groove = helical_ridge(
        thread_z0,
        thread_z1 - thread_z0,
        minor_r,
        major_r,
        SPEC.thread_pitch_mm,
        root_half_angle_deg=76.0,
        crest_half_angle_deg=31.0,
    )
    entry = cylinder(
        tip_z - thread_z1 + 0.15,
        minor_r,
        major_r + 0.45,
        thread_z1,
    )
    body -= bore + groove + entry
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
        for component in tri.split(only_watertight=False)
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
        for component in roundtrip.split(only_watertight=False)
        if len(component.faces) > 4 and abs(float(component.volume)) > 0.01
    ]
    if len(roundtrip_parts) != 2:
        raise RuntimeError(
            f"STL round trip produced {len(roundtrip_parts)} printable bodies"
        )
    if len(roundtrip.split(only_watertight=False)) != 2:
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
        overlap = float((male_seated ^ female_seated).volume())
        if overlap < best_overlap:
            best_phase = float(phase)
            best_overlap = overlap
    for phase in np.arange(best_phase - 10.0, best_phase + 10.1, 1.0):
        female_seated = female.transform(seated_female_transform(float(phase)))
        overlap = float((male_seated ^ female_seated).volume())
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
        + SPEC.flange_thickness_mm
        - SPEC.thread_end_from_outer_face_mm
    )
    female_end = (
        SPEC.assembled_outside_face_spacing_mm
        + SPEC.flange_thickness_mm
        - SPEC.thread_start_from_outer_face_mm
    )
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
            float((male_seated ^ female_moving).volume()),
        )
    return maximum_overlap


def render_design() -> None:
    S = SPEC
    flange_r = S.flange_diameter_mm / 2
    shank_r = S.guide_shank_diameter_mm / 2
    fh = S.flange_thickness_mm
    shank_end = fh + S.guide_shank_length_mm
    tip_z = fh + S.stem_length_from_flange_mm

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=180)
    male_outline = [
        (0, -flange_r), (fh, -flange_r + 0.4),
        (fh, -shank_r), (shank_end, -S.guide_tip_diameter_mm / 2),
        (shank_end, -S.male_stem_root_diameter_mm / 2),
        (tip_z, -S.male_stem_root_diameter_mm / 2),
        (tip_z, S.male_stem_root_diameter_mm / 2),
        (shank_end, S.male_stem_root_diameter_mm / 2),
        (shank_end, S.guide_tip_diameter_mm / 2),
        (fh, shank_r), (fh, flange_r - 0.4), (0, flange_r),
    ]
    ax1.add_patch(Polygon(male_outline, closed=True, facecolor="#dcecf5",
                          edgecolor="#163a5f", linewidth=1.4))
    ax1.axhline(S.bore_diameter_mm / 2, color="#d97706", ls="--", lw=1.1)
    ax1.axhline(-S.bore_diameter_mm / 2, color="#d97706", ls="--", lw=1.1)
    ax1.axvspan(S.thread_start_from_outer_face_mm,
                S.thread_end_from_outer_face_mm,
                color="#2474a6", alpha=0.18, label="coarse male thread")
    ax1.set_aspect("equal", adjustable="box")
    ax1.set_title("Male cap axial profile")
    ax1.set_xlabel("distance from exposed cap face (mm)")
    ax1.set_ylabel("radius (mm)")
    ax1.grid(alpha=0.18)
    ax1.legend(loc="upper right")

    right_face = S.assembled_outside_face_spacing_mm
    male_tip = S.stem_length_from_flange_mm
    female_tip = right_face - S.stem_length_from_flange_mm
    ax2.add_patch(plt.Rectangle(
        (0, -S.bore_diameter_mm / 2),
        right_face,
        S.bore_diameter_mm,
        facecolor="#f3f5f7", edgecolor="#38434f", lw=1.2,
    ))
    ax2.plot([0, male_tip], [0, 0], color="#2474a6", lw=7,
             solid_capstyle="round", label="male stem")
    ax2.plot([female_tip, right_face], [0, 0], color="#d97706", lw=11,
             solid_capstyle="round", label="female receiver")
    ax2.axvline(0, color="#163a5f", lw=5)
    ax2.axvline(right_face, color="#163a5f", lw=5)
    ax2.annotate(
        f"{male_tip - female_tip:.0f} mm stem overlap",
        xy=((male_tip + female_tip) / 2, 0),
        xytext=((male_tip + female_tip) / 2, 11),
        ha="center",
        arrowprops={"arrowstyle": "->", "color": "#38434f"},
    )
    ax2.set_xlim(-8, 120)
    ax2.set_ylim(-22, 22)
    ax2.set_aspect("equal", adjustable="box")
    ax2.set_title("Seated inside the 112 mm through-bore")
    ax2.set_xlabel("assembled axial position (mm)")
    ax2.set_yticks([])
    ax2.legend(loc="lower center", ncol=2)

    fig.suptitle(
        "Rigid Screw-Together Axle-Bore Clamp Plugs",
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
    components = tri.split(only_watertight=False)

    stem_overlap = (
        2 * SPEC.stem_length_from_flange_mm
        - SPEC.assembled_outside_face_spacing_mm
    )
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
        "guide_radial_clearance_mm": (
            SPEC.bore_diameter_mm - SPEC.guide_shank_diameter_mm
        ) / 2,
        "stem_overlap_when_seated_mm": stem_overlap,
        "thread_engagement_when_seated_mm": thread_engagement_when_seated(),
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
        f"seated stems overlap {stem_overlap:.1f} mm; "
        f"best thread phase {phase_deg:.1f} degrees; "
        f"mesh overlap {seated_overlap_mm3:.4f} mm^3; "
        f"thread-path maximum {thread_path_overlap_mm3:.4f} mm^3"
    )


if __name__ == "__main__":
    generate()
