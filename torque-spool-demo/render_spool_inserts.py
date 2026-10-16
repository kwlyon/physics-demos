"""Generate inspection renders for the spool insert deliverable."""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import trimesh
from manifold3d import Manifold

from generate_spool_inserts import (
    ASSEMBLY_Z0,
    INSERT_WIDTH,
    INNER_RADIUS,
    PARAMETERS,
    TARGET_ANGLES,
    export_manifold,
)


ROOT = Path(__file__).resolve().parent
RENDER_DIR = ROOT / "renders"
SOURCE_DIR = ROOT / "Spool_Paradox_Bambu_Print_Kit"


COLORS = {
    "plastic": np.array([0.70, 0.72, 0.76]),
    "tire": np.array([0.10, 0.12, 0.15]),
    "A": np.array([0.10, 0.55, 0.88]),
    "B": np.array([0.96, 0.46, 0.18]),
    "drum": np.array([0.72, 0.74, 0.78]),
}


def load(path: Path) -> trimesh.Trimesh:
    return trimesh.load_mesh(path, process=True, validate=True)


def transformed(mesh: trimesh.Trimesh, matrix) -> trimesh.Trimesh:
    result = mesh.copy()
    result.apply_transform(matrix)
    return result


def translate(mesh: trimesh.Trimesh, xyz) -> trimesh.Trimesh:
    result = mesh.copy()
    result.apply_translation(xyz)
    return result


def add_mesh(ax, mesh, color, alpha=1.0, max_faces=18000, edges=False):
    faces = mesh.faces
    if len(faces) > max_faces:
        faces = faces[np.linspace(0, len(faces) - 1, max_faces).astype(int)]
    tri = mesh.vertices[faces]
    normals = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    normals /= np.maximum(np.linalg.norm(normals, axis=1, keepdims=True), 1e-12)
    light = np.array([-0.25, -0.45, 0.86])
    shade = np.clip(0.50 + 0.46 * np.abs(normals @ light), 0.38, 1.0)
    rgba = np.column_stack(
        (shade[:, None] * np.asarray(color)[None, :], np.full(len(tri), alpha))
    )
    poly = Poly3DCollection(
        tri,
        facecolors=rgba,
        linewidths=0.06 if edges else 0.0,
        edgecolors=(0.05, 0.08, 0.10, 0.20) if edges else "none",
    )
    ax.add_collection3d(poly)


def set_view(ax, meshes, elev=20, azim=-55, pad=0.08, equal=True):
    points = np.vstack([m.bounds for m in meshes])
    lo, hi = points.min(axis=0), points.max(axis=0)
    center = (lo + hi) / 2
    extent = hi - lo
    if equal:
        half = max(extent) * (0.5 + pad)
        ax.set_xlim(center[0] - half, center[0] + half)
        ax.set_ylim(center[1] - half, center[1] + half)
        ax.set_zlim(center[2] - half, center[2] + half)
        ax.set_box_aspect((1, 1, 1))
    else:
        margins = np.maximum(extent * pad, 1.0)
        ax.set_xlim(lo[0] - margins[0], hi[0] + margins[0])
        ax.set_ylim(lo[1] - margins[1], hi[1] + margins[1])
        ax.set_zlim(lo[2] - margins[2], hi[2] + margins[2])
        ax.set_box_aspect(np.maximum(extent, 1.0))
    ax.view_init(elev=elev, azim=azim)
    ax.set_proj_type("ortho")
    ax.set_axis_off()


def save_figure(fig, name):
    fig.patch.set_facecolor("white")
    fig.savefig(RENDER_DIR / name, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def source_assembly():
    male = load(SOURCE_DIR / "Spool_MALE_print_1x.stl")
    female = load(SOURCE_DIR / "Spool_FEMALE_print_1x.stl")
    tire = load(SOURCE_DIR / "Optional_TPU_tire_print_2x.stl")
    # Female is inverted and translated so the two measured connector zones
    # overlap; inner flange faces are then z=9 and z=103 mm.
    female_xform = np.array(
        [[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 112], [0, 0, 0, 1]],
        dtype=float,
    )
    female = transformed(female, female_xform)
    tire_m = translate(tire, (0, 0, 0.5))
    tire_f_xform = female_xform.copy()
    tire_f_xform[2, 3] = 111.5
    tire_f = transformed(tire, tire_f_xform)
    return male, female, tire_m, tire_f


def load_pair(angle):
    a = load(ROOT / f"Spool_Insert_{angle}deg_A.stl")
    b = load(ROOT / f"Spool_Insert_{angle}deg_B.stl")
    return a, b


def render_original():
    male, female, tire_m, tire_f = source_assembly()
    fig = plt.figure(figsize=(8, 7))
    ax = fig.add_subplot(111, projection="3d")
    for mesh in (male, female):
        add_mesh(ax, mesh, COLORS["plastic"], max_faces=14000)
    for mesh in (tire_m, tire_f):
        add_mesh(ax, mesh, COLORS["tire"])
    set_view(ax, [male, female, tire_m, tire_f], elev=18, azim=-52)
    ax.set_title("Original spool assembled with 185 mm OD TPU tires", fontsize=13)
    save_figure(fig, "01_original_spool_with_tires.png")


def render_fitted(angle=50):
    male, female, tire_m, tire_f = source_assembly()
    a, b = load_pair(angle)
    a = translate(a, (0, 0, ASSEMBLY_Z0))
    b = translate(b, (0, 0, ASSEMBLY_Z0))
    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_subplot(111, projection="3d")
    for mesh in (male, female):
        add_mesh(ax, mesh, COLORS["plastic"], alpha=0.28, max_faces=11000)
    for mesh in (tire_m, tire_f):
        add_mesh(ax, mesh, COLORS["tire"], alpha=0.42)
    add_mesh(ax, a, COLORS["A"])
    add_mesh(ax, b, COLORS["B"])
    set_view(ax, [male, female, tire_m, tire_f], elev=17, azim=-48)
    ax.set_title(f"{angle}° insert fitted between the original flanges", fontsize=13)
    save_figure(fig, "02_insert_fitted_to_spool.png")


def render_separated(angle=50):
    a, b = load_pair(angle)
    a = translate(a, (0, 28, 0))
    b = translate(b, (0, -28, 0))
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection="3d")
    add_mesh(ax, a, COLORS["A"], edges=True)
    add_mesh(ax, b, COLORS["B"], edges=True)
    set_view(ax, [a, b], elev=19, azim=-48)
    ax.set_title(f"{angle}° halves separated: four tapered plugs and matching sockets")
    save_figure(fig, "03_halves_separated_plugs.png")


def render_anchor(angle=50):
    a, _ = load_pair(angle)
    r = PARAMETERS["rolling_radius"] * np.cos(np.deg2rad(angle))
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")
    add_mesh(ax, a, COLORS["A"], edges=True)
    ax.set_xlim(-13, 13)
    ax.set_ylim(r - 12, r + 2)
    ax.set_zlim(16, 44)
    ax.set_box_aspect((26, 14, 28))
    ax.view_init(elev=5, azim=90)
    ax.set_proj_type("ortho")
    ax.set_axis_off()
    ax.set_title("Recessed string bay and axial capture post")
    save_figure(fig, "04_string_anchor_closeup.png")


def render_label(angle=50):
    a, b = load_pair(angle)
    r = PARAMETERS["rolling_radius"] * np.cos(np.deg2rad(angle))
    # An exact plane through the engraving depth gives a much clearer
    # inspection image than shaded rendering at this shallow scale.
    fig, axs = plt.subplots(2, 1, figsize=(14, 6.6))
    for ax, mesh, y, color, half in (
        (axs[0], a, 1.0, "#075985", "A"),
        (axs[1], b, -1.0, "#9a3412", "B"),
    ):
        section = mesh.section(
            plane_origin=np.array([0.0, y, INSERT_WIDTH / 2]),
            plane_normal=np.array([0.0, 1.0, 0.0]),
        )
        for entity in section.entities:
            pts = section.vertices[entity.points]
            ax.plot(pts[:, 2], pts[:, 0], color=color, lw=0.9)
        ax.set_xlim(6, INSERT_WIDTH - 6)
        ax.set_ylim(INNER_RADIUS + 0.2, min(r - 0.3, INNER_RADIUS + 5.8))
        ax.set_aspect("equal", adjustable="box")
        ax.set_facecolor("#fafafa")
        ax.set_ylabel(f"Half {half}\nradial X (mm)")
        ax.grid(True, alpha=0.12)
    axs[1].set_xlabel("axial position Z (mm)")
    fig.suptitle(
        f"Both 2.0 mm-deep edge engravings: "
        f"{angle}° FROM HORIZONTAL | r={r:.1f} mm"
    )
    save_figure(fig, "05_engraved_label_closeup.png")


def render_outer_labels(angle=45):
    """Show the actual curved STL surface unwrapped into an easy-to-read map."""
    a, b = load_pair(angle)
    radius = PARAMETERS["rolling_radius"] * np.cos(np.deg2rad(angle))
    span = np.deg2rad(PARAMETERS["outer_label_angle_span_deg"] / 2 + 4)
    fig, axs = plt.subplots(2, 1, figsize=(13, 7.5), constrained_layout=True)
    image = None
    for ax, mesh, center, half in (
        (axs[0], a, np.pi / 2, "A (+Y exterior)"),
        (axs[1], b, -np.pi / 2, "B (-Y exterior)"),
    ):
        xyz = mesh.vertices
        theta = np.arctan2(xyz[:, 1], xyz[:, 0])
        delta = np.arctan2(np.sin(theta - center), np.cos(theta - center))
        arc = -radius * delta
        radial = np.linalg.norm(xyz[:, :2], axis=1)
        face_delta = delta[mesh.faces].mean(axis=1)
        face_z = xyz[mesh.faces, 2].mean(axis=1)
        face_radial = radial[mesh.faces].mean(axis=1)
        keep = (
            (np.abs(face_delta) <= span)
            & (face_z >= 45.0)
            & (face_z <= 82.0)
            & (face_radial >= radius - PARAMETERS["outer_label_depth"] - 0.18)
        )
        faces = mesh.faces[keep]
        polygons = np.stack((arc[faces], xyz[faces, 2]), axis=2)
        depth = np.clip(radius - radial[faces].mean(axis=1), 0.0, 0.9)
        image = PolyCollection(
            polygons,
            array=depth,
            cmap="Blues",
            clim=(0.0, 0.85),
            edgecolors="none",
        )
        ax.add_collection(image)
        ax.autoscale_view()
        ax.set_xlim(-radius * span, radius * span)
        ax.set_ylim(45, 82)
        ax.set_aspect("equal", adjustable="box")
        ax.set_facecolor("#f7fafc")
        ax.set_ylabel(f"{half}\naxial Z (mm)")
        ax.grid(True, alpha=0.12)
    axs[1].set_xlabel("unwrapped circumferential distance (mm)")
    fig.colorbar(image, ax=axs, label="recess depth (mm)", shrink=0.8)
    fig.suptitle(
        f"Large two-line exterior engraving on both halves — {angle}° set",
        fontsize=14,
    )
    save_figure(fig, "08_outer_labels_unwrapped.png")


def render_all_sizes():
    meshes = []
    colors = []
    x_cursor = 0.0
    for angle in TARGET_ANGLES:
        a, b = load_pair(angle)
        r = PARAMETERS["rolling_radius"] * np.cos(np.deg2rad(angle))
        a = translate(a, (x_cursor, 0, 0))
        b = translate(b, (x_cursor, 0, 0))
        meshes.extend((a, b))
        colors.extend((COLORS["A"], COLORS["B"]))
        x_cursor += 2 * r + 24
    fig = plt.figure(figsize=(16, 6))
    ax = fig.add_subplot(111, projection="3d")
    for mesh, color in zip(meshes, colors):
        add_mesh(ax, mesh, color)
    set_view(ax, meshes, elev=18, azim=-58, equal=False)
    ax.set_title("30°, 40°, 45°, 50°, and 60° insert sets (largest to smallest)")
    save_figure(fig, "06_all_five_insert_sizes.png")


def manifold_to_trimesh(model: Manifold) -> trimesh.Trimesh:
    mesh = model.to_mesh()
    return trimesh.Trimesh(
        np.asarray(mesh.vert_properties)[:, :3],
        np.asarray(mesh.tri_verts),
        process=False,
    )


def render_section(angle=50):
    _, b = load_pair(angle)
    # A measured-radius reference drum, clipped to the same negative-Y half as
    # insert B, makes the 0.25 mm radial fit visible on the cut plane.
    drum = Manifold.cylinder(94.0, PARAMETERS["original_drum_radius"],
                             circular_segments=320).translate((0, 0, 9.0))
    half_box = Manifold.cube((200, 100, 120)).translate((-100, -100, 0))
    drum_half = manifold_to_trimesh(drum ^ half_box)
    b = translate(b, (0, 0, ASSEMBLY_Z0))
    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_subplot(111, projection="3d")
    add_mesh(ax, drum_half, COLORS["drum"], edges=True)
    add_mesh(ax, b, COLORS["B"], alpha=0.92, edges=True)
    set_view(ax, [drum_half, b], elev=8, azim=80, equal=False)
    ax.set_title("Sectional fit: 39.0 mm drum, 39.25 mm insert bore")
    save_figure(fig, "07_sectional_fit.png")


def main():
    RENDER_DIR.mkdir(exist_ok=True)
    render_original()
    render_fitted()
    render_separated()
    render_anchor()
    render_label()
    render_all_sizes()
    render_section()
    render_outer_labels()
    print(f"wrote renders to {RENDER_DIR}")


if __name__ == "__main__":
    main()
