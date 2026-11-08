# -*- coding: utf-8 -*-
"""Assemble the journal-format Figure 5: ONE 180 x 240 mm plate, A-O.

This replaces 17_merge_figure5.py.  That first merge simply scaled the legacy
427 mm Figure 05 PNG down to 180 mm, which left its 8-10 pt labels at ~4 pt
(below the 5.6 pt print floor), kept two different headers, duplicated A-D
letters, and had no claim / does-not-support text.  Here both halves are
re-rendered from their own data at journal type sizes and joined on a single
page with ONE header, ONE section rule and ONE three-part footer.

    [ 0 - 15 mm ]  footer: analysis unit / methods / does not support
    [15 -107 mm ]  lower block L-O      (Figure5_lower_LO, 180 x 92)
    [107-112 mm ]  section band + hairline
    [112-225 mm ]  upper block A-K      (Figure5_upper_AK, 180 x 113)
    [225-240 mm ]  shared header: Figure 5 + claim + scope

PNG: pixel-exact paste of the two 600 dpi rasters (no resampling) plus a
transparent text overlay.  PDF: the two SOURCE vector pages are translated onto
one blank page with pypdf and the same overlay is merged last, so every path
and every glyph stays vector; the merged content stream is Flate-compressed.

Known deviations from the package's plate spec, all recorded in the
reproduction note: 240 mm tall (vs the usual 94-152 mm), 15 panels (A-O), and
palette E (teal + plum) retained for A-K instead of the 8-colour board.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from PIL import Image
from pypdf import PdfReader, PdfWriter, PageObject, Transformation

import journal_style as J

ROOT = Path(r"E:/NRFB_atlas_plate_20261104")
FIG = ROOT / "12_空间组神经标记_20261104" / "figures"
STEM = "Figure5_journal_20261104"

UP_PNG, UP_PDF = FIG / "Figure5_upper_AK.png", FIG / "Figure5_upper_AK.pdf"
LO_PNG, LO_PDF = FIG / "Figure5_lower_LO.png", FIG / "Figure5_lower_LO.pdf"

W = 180.0
HEADER_H, UPPER_H, BAND_H, LOWER_H, FOOTER_H = 15.0, 113.0, 5.0, 92.0, 15.0
H = HEADER_H + UPPER_H + BAND_H + LOWER_H + FOOTER_H   # 240 mm
assert abs(H - 240.0) < 1e-9

DPI = 600
PX = DPI / 25.4                     # px per mm


def px(mm: float) -> int:
    return round(mm * PX)


# ------------------------------------------------------------------ text layer
# A claim sentence, not a noun phrase; the subtitle carries scope and n only.
HEADER_NUM = "Figure 5"
HEADER_TITLE = ("PCDH9-positive spots are enriched in the OA NR-FB domain, "
                "yet neural reads cannot map nerve fibres")
# An explicit break keeps the two subtitle lines balanced; letting wrap_mm
# decide leaves "bin50 spots." alone on line 2 (a typographic widow).
HEADER_SUB = ("A-I: Knee2 (high-PPSD), Knee3 (low-PPSD), A4 (control) spatial overlays; "
              "J-K: 5 control vs 2 OA sections.\n"
              "L-O: the same two OA sections, 24,774 and 33,049 bin50 spots; all barcodes matched.")
BAND_LABEL = "L-O   Neural-marker feasibility in the same two OA sections"
FOOTER = (
    "Analysis unit: tissue section. A-I show two OA and one control section; J-K compare five control "
    "with two OA sections (bars = mean, error bars = SD); L-O use the same two OA sections "
    "(24,774 and 33,049 bin50 spots), where bins are observations, not replicates. "
    "Methods: NR-FB domain from the seven-section atlas; L-O inside/outside ratios are tested against a "
    "toroidal-shift null that preserves domain geometry, with 95% intervals built on the log scale "
    "(* P<0.05, ** P<0.001). "
    "Does not support: a neural niche for the NR-FB domain, PCDH9-positive cells contacting nerve "
    "fibres, or any causal link between PCDH9 and innervation."
)

# ------------------------------------------------------------------ PNG layout
im_up = Image.open(UP_PNG).convert("RGB")
im_lo = Image.open(LO_PNG).convert("RGB")
assert im_up.width == im_lo.width, "both halves must share the 180 mm width"

W_PX, H_PX = im_up.width, px(H)
UP_TOP = px(HEADER_H)                                  # from the top edge
# A 600 dpi raster is an integer number of pixels, so 113 mm (2669.3 px) and
# 92 mm (2173.2 px) each carry a sub-pixel remainder.  Anchor the bands to the
# REAL raster heights and let the footer absorb the 1-2 px left over, rather
# than forcing nominal mm boundaries that would tear a row of pixels.
LOW_TOP = UP_TOP + im_up.height + px(BAND_H)
FOOT_TOP = LOW_TOP + im_lo.height
assert 0 < H_PX - FOOT_TOP <= px(FOOTER_H) + 2, "footer band drifted"

base = Image.new("RGB", (W_PX, H_PX), "white")
base.paste(im_up, (0, UP_TOP))
base.paste(im_lo, (0, LOW_TOP))

# Overlay uses an exact pixel-sized figure so its text lands on the same grid
# as the pasted rasters (a plain 180 mm figsize rounds 1 px differently).
fig = plt.figure(figsize=(W_PX / DPI, H_PX / DPI), dpi=DPI)
fig.patch.set_alpha(0.0)

# Guard the header geometry: a two-line title would push the subtitle into the
# A-K block, and a five-line footer would run under the lower plate.
avail = W * 0.985 - (0.008 * W + J.measure_mm(fig, HEADER_NUM, 8.8, "bold") + 1.6)
title_lines = J.wrap_mm(fig, HEADER_TITLE, avail, 8.8).count("\n") + 1
sub_lines = J.wrap_mm(fig, HEADER_SUB, 176.0, 6.9).count("\n") + 1
foot_lines = J.wrap_mm(fig, FOOTER, W - 2 * 0.008 * W - 2.0, 6.0).count("\n") + 1
print(f"header title {title_lines} line(s), subtitle {sub_lines}, footer {foot_lines}")
assert title_lines == 1, "claim sentence wrapped; shorten HEADER_TITLE"
assert sub_lines <= 2, "scope subtitle too long for the 15 mm header band"
assert foot_lines <= 4, "footer too long for the 15 mm footer band"

J.header(fig, HEADER_NUM, HEADER_TITLE,
         J.wrap_mm(fig, HEADER_SUB, 176.0, 6.9),
         x=0.008, y=0.992, size=8.8, subtitle_size=6.9)

# Section rule at the centre of the 5 mm band; the small caption sits above it.
y_line = (H_PX - (UP_TOP + im_up.height + px(BAND_H) / 2.0)) / PX / H
fig.add_artist(Line2D([0.008, 0.992], [y_line, y_line],
                      color="#CDD6DE", lw=0.7, transform=fig.transFigure))
fig.text(0.008, (H_PX - (UP_TOP + im_up.height + px(BAND_H) * 0.72)) / PX / H,
         BAND_LABEL, ha="left", va="center", fontsize=6.9,
         fontweight="bold", color=J.MUTED)

J.footer(fig, FOOTER, x=0.008, y=0.008, size=6.0, linespacing=1.55)

problems = J.check_layout(fig)
print(f"layout check: {len(problems)} problem(s)")
for p in problems[:12]:
    print("  -", p)
assert not problems, "overlay failed the plate layout check"

ov_png = FIG / "_f5_journal_overlay.png"
ov_pdf = FIG / "_f5_journal_overlay.pdf"
fig.savefig(ov_png, dpi=DPI, transparent=True, facecolor="none")
fig.savefig(ov_pdf, transparent=True, facecolor="none")
plt.close(fig)

ov = Image.open(ov_png).convert("RGBA")
assert ov.size == base.size, "overlay/raster pixel grids differ"
Image.alpha_composite(base.convert("RGBA"), ov).convert("RGB").save(
    FIG / f"{STEM}.png", dpi=(DPI, DPI))

# ------------------------------------------------------------------ vector PDF
PT = 72.0 / 25.4
Wpt, Hpt = W * PT, H * PT
page = PageObject.create_blank_page(width=Wpt, height=Hpt)

# Bottom edges in mm, measured from the page foot.  Both source pages are
# already 180 mm wide; s corrects any sub-point rounding in their MediaBox.
UP_BOTTOM = H - (UP_TOP + im_up.height) / PX
LO_BOTTOM = H - FOOT_TOP / PX
for src, bottom in ((UP_PDF, UP_BOTTOM), (LO_PDF, LO_BOTTOM)):
    p = PdfReader(src).pages[0]
    s = Wpt / float(p.mediabox.width)
    page.merge_transformed_page(p, Transformation(ctm=(s, 0, 0, s, 0, bottom * PT)))

ov_page = PdfReader(ov_pdf).pages[0]
sx = Wpt / float(ov_page.mediabox.width)
sy = Hpt / float(ov_page.mediabox.height)
page.merge_transformed_page(ov_page, Transformation(ctm=(sx, 0, 0, sy, 0, 0)))

contents = page.get_contents()
if contents is not None:
    page.replace_contents(contents.flate_encode())
wr = PdfWriter()
wr.add_page(page)
with open(FIG / f"{STEM}.pdf", "wb") as fh:
    wr.write(fh)

ov_png.unlink(missing_ok=True)
ov_pdf.unlink(missing_ok=True)

print(f"upper block : 180 x {UPPER_H:.0f} mm  ({im_up.width} x {im_up.height} px)")
print(f"lower block : 180 x {LOWER_H:.0f} mm  ({im_lo.width} x {im_lo.height} px)")
print(f"full plate  : 180 x {H:.0f} mm  -> {STEM}.png / .pdf (vector)")
for ext in ("png", "pdf"):
    p = FIG / f"{STEM}.{ext}"
    print(f"  {p.name}: {p.stat().st_size / 1e6:.2f} MB")
