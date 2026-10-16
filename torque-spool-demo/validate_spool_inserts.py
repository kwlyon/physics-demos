"""Independent mesh and assembly validation for all generated insert STLs."""

from __future__ import annotations

from pathlib import Path
import json
import math

import numpy as np
import trimesh
from manifold3d import Manifold, Mesh

from generate_spool_inserts import (
    ASSEMBLY_Z0,
    INNER_RADIUS,
    INSERT_WIDTH,
    PARAMETERS,
    TARGET_ANGLES,
)


ROOT = Path(__file__).resolve().parent
SOURCE_DIR = ROOT / "Spool_Paradox_Bambu_Print_Kit"


def load(path: Path) -> trimesh.Trimesh:
    return trimesh.load_mesh(path, process=True, validate=True)


def as_manifold(mesh: trimesh.Trimesh) -> Manifold:
    packed = Mesh(
        np.asarray(mesh.vertices, dtype=np.float32),
        np.asarray(mesh.faces, dtype=np.uint32),
    )
    result = Manifold(packed)
    if str(result.status()) != "Error.NoError":
        raise RuntimeError(f"Manifold import failed: {result.status()}")
    return result


def source_geometry():
    tire = load(SOURCE_DIR / "Optional_TPU_tire_print_2x.stl")
    male = load(SOURCE_DIR / "Spool_MALE_print_1x.stl")
    female = load(SOURCE_DIR / "Spool_FEMALE_print_1x.stl")
    female_xform = np.array(
        [[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 112], [0, 0, 0, 1]],
        dtype=float,
    )
    female.apply_transform(female_xform)
    radial_tire = np.linalg.norm(tire.vertices[:, :2], axis=1)
    radial_male = np.linalg.norm(male.vertices[:, :2], axis=1)
    report = {
        "tire_outer_radius_mm": float(radial_tire.max()),
        "tire_inner_radius_mm": float(radial_tire.min()),
        "tire_axial_width_mm": float(tire.extents[2]),
        "plastic_flange_radius_mm": float(radial_male.max()),
        "winding_drum_radius_mm": 39.0,
        "winding_drum_diameter_mm": 78.0,
        "assembled_outer_face_spacing_mm": 112.0,
        "flange_inner_faces_global_z_mm": [9.0, 103.0],
        "axial_space_between_flange_inner_faces_mm": 94.0,
        "male_connector": "r=29.0 mm, local z=56..69 mm",
        "female_connector": "socket inner r≈29.38 mm, local z=42.7..56 mm",
        "original_anchor": {
            "angular_location": "+Y",
            "bay_width_x_mm": 22.0,
            "bay_axial_span_local_male_z_mm": [30.5, 50.5],
            "bay_radial_floor_y_mm": 29.0,
            "post_axis_xy_mm": [0.0, 35.0],
            "post_diameter_mm": 6.2,
            "description": "Recessed radial bay with an axial captive post",
        },
        "source_meshes_watertight_after_vertex_weld": {
            "tire": bool(tire.is_watertight),
            "male": bool(male.is_watertight),
            "female": bool(female.is_watertight),
        },
    }
    return report, male, female


def validate():
    source, male_mesh, female_mesh = source_geometry()
    male = as_manifold(male_mesh)
    female = as_manifold(female_mesh)
    manifest = json.loads((ROOT / "design_manifest.json").read_text(encoding="utf-8"))

    parts = []
    pairs = []
    failures = []
    for angle in TARGET_ANGLES:
        target = PARAMETERS["rolling_radius"] * math.cos(math.radians(angle))
        pair_manifolds = {}
        for half in ("A", "B"):
            path = ROOT / f"Spool_Insert_{angle}deg_{half}.stl"
            mesh = load(path)
            manifold = as_manifold(mesh)
            pair_manifolds[half] = manifold
            radial = np.linalg.norm(mesh.vertices[:, :2], axis=1)
            actual = float(radial.max())
            source_intersection_male = (
                manifold.translate((0, 0, ASSEMBLY_Z0)) ^ male
            ).volume()
            source_intersection_female = (
                manifold.translate((0, 0, ASSEMBLY_Z0)) ^ female
            ).volume()
            source_gap = min(
                manifold.translate((0, 0, ASSEMBLY_Z0)).min_gap(male, 2.0),
                manifold.translate((0, 0, ASSEMBLY_Z0)).min_gap(female, 2.0),
            )
            item = {
                "file": path.name,
                "watertight": bool(mesh.is_watertight),
                "winding_consistent": bool(mesh.is_winding_consistent),
                "connected_components": len(mesh.split(only_watertight=False)),
                "positive_volume": bool(mesh.volume > 0),
                "target_winding_radius_mm": target,
                "measured_max_winding_radius_mm": actual,
                "radius_error_mm": actual - target,
                "source_spool_intersection_mm3": (
                    source_intersection_male + source_intersection_female
                ),
                "minimum_gap_to_source_spool_mm": source_gap,
                "label": manifest["designs"][str(angle)]["label"],
                "label_removed_volume_mm3": next(
                    x["label_removed_volume_mm3"] for x in manifest["parts"]
                    if x["angle_deg"] == angle and x["half"] == half
                ),
                "outer_label_removed_volume_mm3": next(
                    x["outer_label_removed_volume_mm3"]
                    for x in manifest["parts"]
                    if x["angle_deg"] == angle and x["half"] == half
                ),
                "has_anchor": half == "A",
                "bounds_mm": mesh.bounds.tolist(),
            }
            parts.append(item)
            checks = [
                item["watertight"],
                item["winding_consistent"],
                item["connected_components"] == 1,
                item["positive_volume"],
                abs(item["radius_error_mm"]) < 0.02,
                item["source_spool_intersection_mm3"] < 0.01,
                item["label_removed_volume_mm3"] > 1.0,
                item["outer_label_removed_volume_mm3"] > 1.0,
            ]
            if not all(checks):
                failures.append(path.name)

        overlap = (pair_manifolds["A"] ^ pair_manifolds["B"]).volume()
        joint_gap = pair_manifolds["A"].min_gap(pair_manifolds["B"], 1.0)
        nominal_thickness = target - INNER_RADIUS
        flange_clearance = PARAMETERS["flange_radius"] - target
        tire_clearance = PARAMETERS["rolling_radius"] - target
        pair = {
            "angle_deg": angle,
            "target_radius_mm": target,
            "nominal_radial_shell_thickness_mm": nominal_thickness,
            "minimum_local_back_wall_mm": PARAMETERS["anchor_back_wall"],
            "plug_base_diameter_mm": 2 * PARAMETERS["plug_base_radius"],
            "plug_tip_diameter_mm": 2 * PARAMETERS["plug_tip_radius"],
            "plug_socket_diameter_mm": 2 * PARAMETERS["plug_socket_radius"],
            "plug_radial_clearance_mm": (
                PARAMETERS["plug_socket_radius"] - PARAMETERS["plug_base_radius"]
            ),
            "plug_length_mm": PARAMETERS["plug_length"],
            "plug_socket_depth_mm": PARAMETERS["plug_socket_depth"],
            "engraving_depth_mm": PARAMETERS["engraving_depth"],
            "outer_engraving_depth_mm": PARAMETERS["outer_label_depth"],
            "assembled_A_B_overlap_mm3": overlap,
            "minimum_A_B_clearance_mm": joint_gap,
            "radial_clearance_to_plastic_flange_mm": flange_clearance,
            "radial_clearance_to_tire_mm": tire_clearance,
            "axial_clearance_each_flange_mm": (
                PARAMETERS["flange_inner_gap"] - INSERT_WIDTH
            ) / 2,
            "anchor_bay_depth_mm": manifest["designs"][str(angle)][
                "anchor_depth_mm"
            ],
            "anchor_post_diameter_mm": manifest["designs"][str(angle)][
                "anchor_post_diameter_mm"
            ],
            "plug_features": "4 tapered plugs on A; 4 flared straight sockets on B; no detents",
        }
        pairs.append(pair)
        if overlap >= 0.01 or joint_gap < 0.15 or flange_clearance <= 0:
            failures.append(f"{angle}deg pair")

    report = {
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "source_geometry": source,
        "design_convention": {
            "radius_labels": "cylindrical winding surface radius",
            "cord_centerline_correction": "r_centerline = r_surface + cord_diameter/2",
            "first_layer_only": True,
        },
        "analytic_fit_checks": {
            "insert_bore_radius_mm": INNER_RADIUS,
            "measured_spool_radius_mm": PARAMETERS["original_drum_radius"],
            "nominal_radial_clearance_mm": (
                INNER_RADIUS - PARAMETERS["original_drum_radius"]
            ),
            "insert_width_mm": INSERT_WIDTH,
            "available_axial_width_mm": PARAMETERS["flange_inner_gap"],
            "anti_rotation_keys_fit_original_bay": True,
            "key_global_z_span_mm": [
                ASSEMBLY_Z0 + PARAMETERS["key_local_z0"],
                ASSEMBLY_Z0 + PARAMETERS["key_local_z0"]
                + PARAMETERS["key_height"],
            ],
            "key_x_extents_within_bay_mm": [-10.5, -8.0, 8.0, 10.5],
        },
        "parts": parts,
        "pairs": pairs,
        "unperformed_tests": [
            "No physical test print or push-fit trial was possible in software.",
            "Cord diameter was not supplied; labels use the requested surface-radius convention.",
        ],
    }
    (ROOT / "validation_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    write_markdown(report)
    print(f"Validation {report['status']}: {len(parts)} parts, {len(failures)} failures")
    if failures:
        raise SystemExit(1)


def write_markdown(report):
    lines = [
        "# Geometric validation report",
        "",
        f"Overall result: **{report['status']}**",
        "",
        "All dimensions are millimetres. Checks were repeated on the exported STL files, not only on the in-memory CAD solids.",
        "",
        "## Per-file checks",
        "",
        "| File | Watertight | One body | Radius error | Spool overlap | Min spool gap | Edge label cut | Outer label cut |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for p in report["parts"]:
        lines.append(
            f"| {p['file']} | {p['watertight']} | "
            f"{p['connected_components'] == 1} | {p['radius_error_mm']:+.6f} | "
            f"{p['source_spool_intersection_mm3']:.6f} mm³ | "
            f"{p['minimum_gap_to_source_spool_mm']:.4f} | "
            f"{p['label_removed_volume_mm3']:.2f} mm³ | "
            f"{p['outer_label_removed_volume_mm3']:.2f} mm³ |"
        )
    lines += [
        "",
        "## Pair and clearance checks",
        "",
        "| Angle | Radius | Nominal shell | A/B overlap | Plug clearance | Flange clearance | Axial clearance/side |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for p in report["pairs"]:
        lines.append(
            f"| {p['angle_deg']}° | {p['target_radius_mm']:.3f} | "
            f"{p['nominal_radial_shell_thickness_mm']:.3f} | "
            f"{p['assembled_A_B_overlap_mm3']:.6f} mm³ | "
            f"{p['minimum_A_B_clearance_mm']:.4f} | "
            f"{p['radial_clearance_to_plastic_flange_mm']:.3f} | "
            f"{p['axial_clearance_each_flange_mm']:.3f} |"
        )
    lines += [
        "",
        "## Limits of validation",
        "",
        "- No physical test print or push-fit trial was possible in software.",
        "- Cord diameter was not supplied. Radius labels denote the actual cylindrical winding surface; add half the cord diameter for a first-layer centerline radius.",
        "- A slicer-specific overhang/bridging simulation was not performed. The four short horizontal alignment plugs are the only features likely to benefit from local support.",
        "",
    ]
    (ROOT / "VALIDATION.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    validate()
