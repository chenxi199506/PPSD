# PPSD — Main-Text Figure Plotting Code

Plotting source code for the main-text figures of the OAI-PPSD / PCDH9
manuscript. Python and R scripts, 180 mm journal-style plates.

**This repository contains plotting code only.** Source datasets, rendered
figures, figure legends and manuscript text are not included.

> The associated manuscript has not yet been published. No license is granted;
> all rights are reserved. Please contact the authors before any reuse.

## Layout

The original working tree had very deeply nested Chinese directory names. They
are shortened here; the mapping is:

| In this repository | Original directory under `01_正文图/` |
|---|---|
| `figure_source_archive/` | `20261108_正文图作图源归档/` |
| `editable_package/minimal_repro/` | `20261107_投稿图版可编辑包/最小复现总包/24_图版01-07_最小复现总包_20261106/` |
| `editable_package/composite/` | `20261107_投稿图版可编辑包/合稿/` |
| `editable_package/` (root scripts) | `20261107_投稿图版可编辑包/` |
| `nc_revision/` | `20261108_NC正文图审阅与图注/整改产物/_scripts/` |

Subdirectories under `editable_package/minimal_repro/` are named after the
seven main-text figures (`01_OAI` ... `07_SynovialFluid`); the Figure 2 sources
are not part of this public archive.

## Which scripts draw which figure

| Figure | Main scripts |
|---|---|
| 1 · OAI pain-structure discordance | `figure_source_archive/Fig1_.../scripts/*.R`, `editable_package/minimal_repro/01_OAI/scripts/*.R`, `nc_revision/build_fig1_nc.py` |
| 2 · TKA postoperative outcomes | Not included in this public archive |
| 3 · single-cell NR-FB atlas | `editable_package/minimal_repro/03_NRFB_sc/**`, `editable_package/composite/Figure3_180mm_20261107/**` |
| 4 · tissue NR-FB / PCDH9 | `editable_package/minimal_repro/04_Tissue/Figure4_data_package_20261106/scripts/**` |
| 5 · spatial localisation | `editable_package/minimal_repro/05_Spatial/scripts/**` |
| 6 · knockdown / MEA | `editable_package/minimal_repro/06_Experiments/scripts/**`, `editable_package/composite/Figure6_F3配色定稿_20261108/src/**` |
| 7 · synovial fluid PCDH9 | `editable_package/minimal_repro/07_SynovialFluid/scripts/**` |

`editable_package/minimal_repro/` also holds the package tooling
(`build_package.py`, `make_portable.py`, `check_package.py`,
`rebuild_manifest.py`); `editable_package/` root holds version-switch and
layout-check helpers. `nc_revision/` holds the post-review Figure 1 rebuild,
layout checks and the shared `nc_style.py`.

Several directories are successive versions or reproduction packages of the
same plate (e.g. three variants of `build_F3_P08_portable.py` and several
slightly different `journal_style.py` copies). They are kept as-is for
traceability. The final versions are those under `figure_source_archive/` and
`nc_revision/`.

## Requirements

- Python 3.9+ with `matplotlib`, `numpy`, `scipy`, `pandas`, `Pillow`
- R 4.x with `ggplot2`, `grid`, `jsonlite`, `patchwork`, `ragg`, `splines`, `svglite`
- Arial (some scripts fall back to DejaVu Sans; a few reference
  `C:/Windows/Fonts/` and need adjusting on other systems)

## Configuration before running

The scripts originally referenced the authors' local absolute paths. In this
public archive they are replaced by placeholders: `project_root/`,
`ppsd_workspace/`, `experiment_root/`, `home_root/`. Point them at your own copy
of the working tree before running.

Input data - `data.json`, `stats.json`, the CSV / TSV source tables, original
workbooks, single-cell objects and calibration tables - are **not** distributed
here. Treat this repository as a **source-code record**, not a turnkey
reproduction package.

`build_gallery.py` (an HTML preview-page generator for Figure 1 candidates,
embedding internal notes about display-only simulated data) is deliberately
not distributed. All Figure 2 scripts - the two cohort redraw sources and the
post-review NC layout rebuild - are likewise omitted; some package-tooling
files still reference their former paths.

## Status

83 scripts: 71 Python, 12 R, about 26,150 lines. All Python files pass a
syntax compile check; R scripts are provided as-is.