"""Generate low-profile rope-hook accessories for the spool anchor posts.

The hook is a one-piece, non-snap J profile.  Its tapered nose is threaded
through the narrow opening beside the anchor post and the part is rotated
around the post.  The long tail then lies tangent to the spool.  A raised,
smooth eyelet on the tail accepts the rope without putting a bulky knot at
the post itself.

Two sizes are exported because the 60-degree insert uses a 4.0 mm post while
the original spool and the 30/40/45/50-degree inserts use a 6.2 mm post.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import trimesh
from manifold3d import CrossSection, FillRule, Manifold


ROOT = Path(__file__).resolve().parent
RENDER_DIR = ROOT / "renders"


@dataclass(frozen=True)
class HookSpec:
    name: str
    post_diameter_mm: float
    anchor_entry_gap_mm: float = 0.90
    post_clearance_mm: float = 0.25
    main_hook_wall_mm: float = 1.60
    tapered_tip_mm: float = 0.65
    axial_width_mm: float = 10.0
    tail_radial_thickness_mm: float = 1.80
    eye_hole_diameter_mm: float = 5.20


SPECS = (
    HookSpec("Low_Profile_Rope_Hook_6p2mm_Post", 6.2),
    HookSpec(
        "Low_Profile_Rope_Hook_4p0mm_Post",
        4.0,
        main_hook_wall_mm=1.35,
    ),
)


def cylinder_along_y(
    height: float,
    radius_low: float,
    radius_high: float,
    x: float,
    y: float,
    z: float,
) -> Manifold:
    model = Manifold.cylinder(
        height,
        radius_low,
        radius_high,
        circular_segments=96,
    )
    matrix = np.array(
        [
            [1, 0, 0, x],
            [0, 0, 1, y],
            [0, 1, 0, z],
        ],
        dtype=float,
    )
    return model.transform(matrix)


def hook_band(spec: HookSpec) -> Manifold:
    """Tapered J band in XY, extruded along the axial Z direction."""
    inner = spec.post_diameter_mm / 2 + spec.post_clearance_mm
    start_deg = 155.0
    end_deg = 420.0
    angles = np.linspace(start_deg, end_deg, 150)
    outer_points = []
    for angle in angles:
        ramp = min(1.0, max(0.0, (angle - start_deg) / 42.0))
        wall = spec.tapered_tip_mm + ramp * (
            spec.main_hook_wall_mm - spec.tapered_tip_mm
        )
        radius = inner + wall
        theta = math.radians(angle)
        outer_points.append((radius * math.cos(theta), radius * math.sin(theta)))
    inner_points = []
    for angle in angles[::-1]:
        theta = math.radians(angle)
        inner_points.append((inner * math.cos(theta), inner * math.sin(theta)))
    section = CrossSection([outer_points + inner_points], FillRule.NonZero)
    return section.extrude(spec.axial_width_mm).translate(
        (0, 0, -spec.axial_width_mm / 2)
    )


def make_hook(spec: HookSpec) -> tuple[Manifold, dict]:
    post_radius = spec.post_diameter_mm / 2
    inner_radius = post_radius + spec.post_clearance_mm
    surface_y = post_radius + spec.anchor_entry_gap_mm
    plate_y0 = surface_y + 0.10
    plate_y1 = plate_y0 + spec.tail_radial_thickness_mm
    half_width = spec.axial_width_mm / 2

    band = hook_band(spec)

    # A compact transition joins the hook end to the tangent plate without
    # closing the J opening used during installation.
    connector_points = [
        (1.2, inner_radius * 0.76),
        (3.4, plate_y0 - 0.55),
        (8.0, plate_y0),
        (8.0, plate_y1),
        (2.0, plate_y1 - 0.35),
    ]
    connector = CrossSection([connector_points], FillRule.NonZero).extrude(
        spec.axial_width_mm
    ).translate((0, 0, -half_width))

    # Tangent plate with a rounded trailing end.
    plate = Manifold.cube((19.0, spec.tail_radial_thickness_mm,
                           spec.axial_width_mm)).translate(
        (5.0, plate_y0, -half_width)
    )
    round_end = cylinder_along_y(
        spec.tail_radial_thickness_mm,
        half_width,
        half_width,
        24.0,
        plate_y0,
        0.0,
    )
    body = band + connector + plate + round_end

    # Through-eye plus a low, tapered annular rim.  The 5.2 mm clear opening
    # handles common 2-3 mm demonstration cord and the flared rim avoids a
    # sharp rope-bearing edge.
    eye_x = 23.0
    eye_inner = spec.eye_hole_diameter_mm / 2
    eye_hole = cylinder_along_y(
        spec.tail_radial_thickness_mm + 3.2,
        eye_inner,
        eye_inner,
        eye_x,
        plate_y0 - 0.4,
        0.0,
    )
    body -= eye_hole
    eye_outer = cylinder_along_y(
        2.35,
        4.70,
        4.05,
        eye_x,
        plate_y1 - 0.20,
        0.0,
    )
    eye_bore = cylinder_along_y(
        2.75,
        eye_inner,
        eye_inner,
        eye_x,
        plate_y1 - 0.40,
        0.0,
    )
    body += eye_outer - eye_bore

    meta = {
        "file": f"{spec.name}.stl",
        "post_diameter_mm": spec.post_diameter_mm,
        "post_radial_clearance_mm": spec.post_clearance_mm,
        "hook_inner_radius_mm": inner_radius,
        "tapered_leading_tip_mm": spec.tapered_tip_mm,
        "anchor_entry_gap_mm": spec.anchor_entry_gap_mm,
        "tangent_plate_radial_thickness_mm": spec.tail_radial_thickness_mm,
        "axial_width_mm": spec.axial_width_mm,
        "eye_clear_diameter_mm": spec.eye_hole_diameter_mm,
        "eye_projection_beyond_plate_mm": 2.15,
        "spool_surface_relative_y_mm": surface_y,
        "plate_inner_face_relative_y_mm": plate_y0,
    }
    return body, meta


def export(model: Manifold, path: Path) -> trimesh.Trimesh:
    if model.is_empty() or str(model.status()) != "Error.NoError":
        raise RuntimeError(f"Invalid hook manifold: {model.status()}")
    mesh = model.to_mesh()
    tri = trimesh.Trimesh(
        np.asarray(mesh.vert_properties, dtype=float)[:, :3],
        np.asarray(mesh.tri_verts, dtype=np.int64),
        process=False,
    )
    tri.export(path)
    return tri


def add_mesh(ax, mesh: trimesh.Trimesh, color):
    tri = mesh.vertices[mesh.faces]
    normals = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    normals /= np.maximum(np.linalg.norm(normals, axis=1, keepdims=True), 1e-12)
    light = np.array([-0.25, -0.45, 0.86])
    shade = np.clip(0.48 + 0.48 * np.abs(normals @ light), 0.35, 1.0)
    rgba = np.column_stack(
        (shade[:, None] * np.asarray(color)[None, :], np.ones(len(tri)))
    )
    ax.add_collection3d(
        Poly3DCollection(tri, facecolors=rgba, edgecolors="none")
    )


def render(meshes: list[trimesh.Trimesh], metadata: list[dict]) -> None:
    RENDER_DIR.mkdir(exist_ok=True)
    fig = plt.figure(figsize=(13, 9))
    for index, (mesh, meta) in enumerate(zip(meshes, metadata)):
        ax3 = fig.add_subplot(2, 2, index + 1, projection="3d")
        add_mesh(ax3, mesh, np.array([0.12, 0.56, 0.82]))
        bounds = mesh.bounds
        center = bounds.mean(axis=0)
        half = max(bounds[1] - bounds[0]) * 0.58
        ax3.set_xlim(center[0] - half, center[0] + half)
        ax3.set_ylim(center[1] - half, center[1] + half)
        ax3.set_zlim(center[2] - half, center[2] + half)
        ax3.set_box_aspect((1, 1, 1))
        ax3.view_init(elev=26, azim=-58)
        ax3.set_proj_type("ortho")
        ax3.set_axis_off()
        ax3.set_title(f"Hook for {meta['post_diameter_mm']:.1f} mm post")

        ax2 = fig.add_subplot(2, 2, index + 3)
        section = mesh.section(
            plane_origin=np.array([0.0, 0.0, 0.0]),
            plane_normal=np.array([0.0, 0.0, 1.0]),
        )
        for entity in section.entities:
            pts = section.vertices[entity.points]
            ax2.plot(pts[:, 0], pts[:, 1], color="#075985", lw=1.4)
        post = Circle(
            (0, 0),
            meta["post_diameter_mm"] / 2,
            facecolor="#9ca3af",
            edgecolor="#374151",
            lw=1.2,
        )
        ax2.add_patch(post)
        sy = meta["spool_surface_relative_y_mm"]
        ax2.axhline(sy, color="#dc2626", ls="--", lw=1.0,
                    label="spool surface")
        ax2.fill_between([-7, 31], sy - 0.25, sy, color="#fecaca", alpha=0.5)
        ax2.set_xlim(-7, 31)
        ax2.set_ylim(-7, 11)
        ax2.set_aspect("equal", adjustable="box")
        ax2.grid(True, alpha=0.15)
        ax2.set_xlabel("tangential direction (mm)")
        ax2.set_ylabel("radial direction (mm)")
        ax2.legend(loc="lower right", frameon=False)
        ax2.set_title("Installed plan view: tail lies tangent to spool")
    fig.suptitle(
        "Low-profile thread-and-rotate rope hooks with raised smooth eyelets",
        fontsize=14,
    )
    fig.tight_layout()
    fig.savefig(
        RENDER_DIR / "09_low_profile_rope_hooks.png",
        dpi=220,
        bbox_inches="tight",
        facecolor="white",
    )
    plt.close(fig)


def main() -> None:
    meshes = []
    records = []
    failures = []
    for spec in SPECS:
        model, meta = make_hook(spec)
        path = ROOT / meta["file"]
        mesh = export(model, path)
        components = len(mesh.split(only_watertight=False))
        checks = {
            "watertight": bool(mesh.is_watertight),
            "winding_consistent": bool(mesh.is_winding_consistent),
            "one_connected_body": components == 1,
            "positive_volume": bool(mesh.volume > 0),
            "tip_fits_measured_entry_gap": (
                spec.tapered_tip_mm < spec.anchor_entry_gap_mm
            ),
            "eye_clearance_suitable_for_2_to_3_mm_cord": (
                spec.eye_hole_diameter_mm >= 5.0
            ),
        }
        if not all(checks.values()):
            failures.append(spec.name)
        meta.update(
            {
                "vertices": len(mesh.vertices),
                "triangles": len(mesh.faces),
                "volume_mm3": float(mesh.volume),
                "bounds_mm": mesh.bounds.tolist(),
                "checks": checks,
            }
        )
        meshes.append(mesh)
        records.append(meta)
        print(
            f"wrote {path.name}: {len(mesh.vertices)} vertices, "
            f"{len(mesh.faces)} triangles"
        )
    report = {
        "status": "PASS" if not failures else "FAIL",
        "design_intent": (
            "Thread the tapered J tip beside the post, rotate around the post, "
            "and lay the eyelet tail tangent to the spool."
        ),
        "parts": records,
        "physical_test_required": True,
        "unperformed_test": (
            "A printed hook has not been physically threaded through the anchor entry."
        ),
    }
    (ROOT / "rope_hook_validation.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    render(meshes, records)
    if failures:
        raise SystemExit(f"Hook validation failed: {failures}")
    print("Hook validation PASS")


if __name__ == "__main__":
    main()
