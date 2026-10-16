"""Measure the supplied spool meshes without modifying them."""

from __future__ import annotations

from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np
import trimesh


SOURCE_DIR = Path(__file__).resolve().parent / "Spool_Paradox_Bambu_Print_Kit"
FILES = {
    "tire": SOURCE_DIR / "Optional_TPU_tire_print_2x.stl",
    "female": SOURCE_DIR / "Spool_FEMALE_print_1x.stl",
    "male": SOURCE_DIR / "Spool_MALE_print_1x.stl",
}


def radial_profile(mesh: trimesh.Trimesh, axial_axis: int, bins: int = 100):
    axes = [0, 1, 2]
    axes.remove(axial_axis)
    v = mesh.vertices
    # The supplied parts are centered on their symmetric X/Y bounds.  A vertex
    # median is biased by locally dense features such as the string clip.
    center = (mesh.bounds[0, axes] + mesh.bounds[1, axes]) / 2
    radial = np.linalg.norm(v[:, axes] - center, axis=1)
    axial = v[:, axial_axis]
    edges = np.linspace(axial.min(), axial.max(), bins + 1)
    rows = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        sel = (axial >= lo) & (axial < hi)
        if np.any(sel):
            rr = radial[sel]
            rows.append(
                {
                    "x": float((lo + hi) / 2),
                    "n": int(sel.sum()),
                    "r_min": float(rr.min()),
                    "r_p05": float(np.quantile(rr, 0.05)),
                    "r_med": float(np.median(rr)),
                    "r_p95": float(np.quantile(rr, 0.95)),
                    "r_max": float(rr.max()),
                }
            )
    return center, rows


def inspect(name: str, path: Path):
    mesh = trimesh.load_mesh(path, process=True, validate=True)
    ext = mesh.extents
    # The spool and tire axes are along their smallest overall extent.
    axial_axis = int(np.argmin(ext))
    center, profile = radial_profile(mesh, axial_axis)
    components = mesh.split(only_watertight=False)
    sections = []
    for z in np.linspace(mesh.bounds[0, axial_axis] + 0.1,
                         mesh.bounds[1, axial_axis] - 0.1, 24):
        origin = mesh.bounds.mean(axis=0)
        origin[axial_axis] = z
        normal = np.zeros(3)
        normal[axial_axis] = 1.0
        section = mesh.section(plane_origin=origin, plane_normal=normal)
        if section is None:
            continue
        pts = np.asarray(section.vertices)
        rr = np.linalg.norm(pts[:, [i for i in range(3) if i != axial_axis]] - center, axis=1)
        sections.append({"z": float(z), "r_min": float(rr.min()),
                         "r_max": float(rr.max()), "segments": int(len(section.entities))})
    z_levels = []
    for z in np.unique(np.round(mesh.vertices[:, axial_axis], 3)):
        vv = mesh.vertices[np.isclose(mesh.vertices[:, axial_axis], z, atol=0.0006)]
        rr = np.linalg.norm(vv[:, [i for i in range(3) if i != axial_axis]] - center, axis=1)
        z_levels.append({"z": float(z), "count": int(len(vv)),
                         "r_min": float(rr.min()), "r_max": float(rr.max())})
    return {
        "name": name,
        "path": str(path),
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
        "bounds": mesh.bounds.tolist(),
        "extents": ext.tolist(),
        "axial_axis": "XYZ"[axial_axis],
        "radial_center_other_axes": center.tolist(),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "euler_number": int(mesh.euler_number),
        "volume": float(mesh.volume),
        "body_count": len(components),
        "component_extents": [c.extents.tolist() for c in components[:20]],
        "top_vertex_radii": [
            {"radius": float(r), "count": int(n)}
            for r, n in sorted(
                zip(*np.unique(np.round(np.linalg.norm(
                    mesh.vertices[:, [i for i in range(3) if i != axial_axis]] - center,
                    axis=1), 3), return_counts=True)),
                key=lambda pair: pair[1], reverse=True
            )[:20]
        ],
        "sections": sections,
        "z_levels": z_levels,
        "radial_profile": profile,
    }


def add_mesh(ax, mesh, title, elev, azim, max_faces=12000):
    faces = mesh.faces
    if len(faces) > max_faces:
        faces = faces[np.linspace(0, len(faces) - 1, max_faces).astype(int)]
    tri = mesh.vertices[faces]
    poly = Poly3DCollection(tri, linewidths=0.02, edgecolors=(0.12, 0.16, 0.2, 0.18))
    normals = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    normals /= np.maximum(np.linalg.norm(normals, axis=1, keepdims=True), 1e-12)
    light = np.array([0.35, -0.55, 0.76])
    brightness = np.clip(0.48 + 0.45 * np.abs(normals @ light), 0.35, 0.98)
    base = np.array([0.16, 0.52, 0.80])
    colors = np.column_stack([brightness[:, None] * base, np.full(len(tri), 1.0)])
    poly.set_facecolor(colors)
    ax.add_collection3d(poly)
    b = mesh.bounds
    center = b.mean(axis=0)
    half = mesh.extents.max() / 2 * 1.08
    ax.set_xlim(center[0] - half, center[0] + half)
    ax.set_ylim(center[1] - half, center[1] + half)
    ax.set_zlim(center[2] - half, center[2] + half)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_proj_type("ortho")
    ax.set_title(title)
    ax.set_axis_off()


def render_source_montage():
    meshes = {name: trimesh.load_mesh(path, process=True, validate=True)
              for name, path in FILES.items()}
    fig = plt.figure(figsize=(14, 9), dpi=160)
    views = [(22, 35), (0, 0)]
    plot_no = 1
    for name in ("male", "female", "tire"):
        for elev, azim in views:
            ax = fig.add_subplot(3, 2, plot_no, projection="3d")
            add_mesh(ax, meshes[name], f"{name}: elev {elev}°, azim {azim}°", elev, azim)
            plot_no += 1
    fig.tight_layout()
    fig.savefig(Path(__file__).with_name("source_mesh_montage.png"), bbox_inches="tight")
    plt.close(fig)

    fig = plt.figure(figsize=(15, 8), dpi=180)
    plot_no = 1
    for name in ("male", "female"):
        mesh = meshes[name]
        radial = np.linalg.norm(mesh.vertices[:, :2], axis=1)
        keep = np.all(radial[mesh.faces] < 52.0, axis=1)
        core = trimesh.Trimesh(mesh.vertices.copy(), mesh.faces[keep], process=False)
        for elev, azim in ((18, 30), (0, 0), (90, -90)):
            ax = fig.add_subplot(2, 3, plot_no, projection="3d")
            add_mesh(ax, core, f"{name} core", elev, azim, max_faces=20000)
            plot_no += 1
    fig.tight_layout()
    fig.savefig(Path(__file__).with_name("source_core_closeups.png"), bbox_inches="tight")
    plt.close(fig)

    male = meshes["male"]
    cent = male.triangles_center
    keep = ((np.abs(cent[:, 0]) < 15) & (cent[:, 1] > 24) &
            (cent[:, 2] > 20) & (cent[:, 2] < 57))
    anchor = trimesh.Trimesh(male.vertices.copy(), male.faces[keep], process=False)
    fig = plt.figure(figsize=(15, 5), dpi=200)
    for i, (elev, azim) in enumerate(((10, -90), (0, 0), (90, -90)), start=1):
        ax = fig.add_subplot(1, 3, i, projection="3d")
        add_mesh(ax, anchor, "male string anchor region", elev, azim, max_faces=20000)
    fig.tight_layout()
    fig.savefig(Path(__file__).with_name("source_anchor_closeup.png"), bbox_inches="tight")
    plt.close(fig)

    # Exact mesh/plane intersections reveal the recessed clip far more clearly
    # than a translucent triangle view.
    cuts = [
        (np.array([0, 0, 1.0]), np.array([0, 0, 40.0]), (0, 1), "XY at z=40 mm"),
        (np.array([1.0, 0, 0]), np.array([0, 0, 40.0]), (1, 2), "YZ at x=0 mm"),
        (np.array([0, 1.0, 0]), np.array([0, 35.0, 40.0]), (0, 2), "XZ at y=35 mm"),
    ]
    fig, axs = plt.subplots(1, 3, figsize=(15, 5), dpi=180)
    for ax, (normal, origin, dims, title) in zip(axs, cuts):
        section = male.section(plane_origin=origin, plane_normal=normal)
        for entity in section.entities:
            pts = section.vertices[entity.points]
            ax.plot(pts[:, dims[0]], pts[:, dims[1]], color="#1565a9", lw=1.3)
        ax.set_aspect("equal", adjustable="box")
        ax.grid(True, alpha=0.2)
        ax.set_title(title)
        ax.set_xlabel("XYZ"[dims[0]] + " (mm)")
        ax.set_ylabel("XYZ"[dims[1]] + " (mm)")
    axs[0].set_xlim(-15, 15); axs[0].set_ylim(25, 42)
    axs[1].set_xlim(25, 42); axs[1].set_ylim(20, 58)
    axs[2].set_xlim(-15, 15); axs[2].set_ylim(20, 58)
    fig.tight_layout()
    fig.savefig(Path(__file__).with_name("source_anchor_sections.png"), bbox_inches="tight")
    plt.close(fig)


def main():
    report = {name: inspect(name, path) for name, path in FILES.items()}
    out = Path(__file__).with_name("source_mesh_inspection.json")
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    for name, data in report.items():
        print(f"\n{name.upper()}: {data['path']}")
        print(f"  extents={np.round(data['extents'], 4)} axis={data['axial_axis']}")
        print(
            f"  verts={data['vertices']} faces={data['faces']} "
            f"watertight={data['watertight']} bodies={data['body_count']}"
        )
        print(f"  bounds={np.round(data['bounds'], 4)}")
        print(f"  common radii={data['top_vertex_radii'][:10]}")
        print(f"  sections={data['sections']}")
        print("  selected radial-profile bins (axial, r05, r50, r95, rmax):")
        p = data["radial_profile"]
        for row in p[:: max(1, len(p) // 20)]:
            print(
                f"    {row['x']:8.3f} {row['r_p05']:8.3f} {row['r_med']:8.3f} "
                f"{row['r_p95']:8.3f} {row['r_max']:8.3f} n={row['n']}"
            )
    render_source_montage()


if __name__ == "__main__":
    main()
