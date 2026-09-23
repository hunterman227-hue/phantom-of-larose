# All-P Overlay Report — 2026-09-16

## What was done
Reviewed **all 14 P-mark coin photos** on file. Obverse-to-obverse and reverse-to-reverse comparison.
D-mint photos, screenshots, group shots, duplicates, and blurry context images were excluded (list below).

## Alignment: honest result
I attempted pixel-level overlay (SIFT, template matching over rotation/scale, ECC refinement,
manual landmarks, edge matching). **It did not converge reliably.** The source photos vary too much:
different phones, dates, lighting, exposure, rotation, crop, and red annotation markup drawn over
the features. Automated methods matched wrong regions; manual point correspondences were ambiguous
because the tiny dots look alike and sit nearly on one line (degenerate triangles → sliver warps).

What IS reliable: side-by-side comparison at matched presentation. All 10 P obverses and all 4 P
reverses are in the contact sheets, with the Die-1 markers annotated. The repeatability conclusion
below rests on the marks appearing at the **same design positions** across photos, verified by eye —
not on a pixel blend.

Files in `notes/overlays/all-p-overlay/`:
- `obverse_all_10_contact.jpg` — all 10 P obverses
- `reverse_all_4_contact.jpg` — all 4 P reverses
- `obverse_die1_markers_annotated.jpg` — mosquito bite / ant bite / splenter marked on tight obverses
- `reverse_phantom_annotated.jpg` — duck head / crack features marked on reverses
- `repeatability.csv` — per-photo feature visibility table
- `reverse_zonemap.jpg` — full reverse 012 with phantom zone indicated (reviewed, not pixel-blended:
  its framing is too different for a trustworthy blend)

## Five findings
1. **The raised dots repeat.** A small raised dot at the finger/wrist junction (the "mosquito bite")
   is visible in 001, 002, 003, 006, and 016 — five separate photos, same design spot. High confidence
   the feature is real, not a photo artifact.
2. **The wavy ridge repeats.** A wavy raised ridge on the arm below the hand (the "splenter") appears
   in 001, 002, 003, 005, 006, and 016 at the same design position. High confidence it is real.
3. **The ant-bite dot is less certain.** A second small dot on the arm/drapery is marked in several
   photos, but it is unclear whether all marks point at the *same* dot — there may be more than one
   small dot in that area. Medium confidence.
4. **Reverse: possible progression, not proven.** 011 and 013 show a duck-head-like shape where the
   sail lines meet (possible early stage). 014 shows a longer, crack-like elongated feature in the
   same zone (possible middle/later stage). The framings differ too much to prove these are stages of
   one growing feature versus different lighting of the same feature. **No usable half-phantom or
   full-phantom photograph is on file.**
5. **Mechanism stays provisional.** Repeatability at the same design position supports a **die origin**
   (something in the die, not random damage). It does NOT decide between a die chip and Pete Apple's
   die-flow-wave interpretation — both would repeat at the same spot. The red arrows and lines in the
   photos are markup, not coin features, and they complicated the alignment.

## Photos reviewed (14)
Obverses (10): 001, 002, 003, 005, 006, 007, 008, 009, 010, 016.
Reverses (4): 011, 012, 013, 014.
Note: 012 (full golden reverse) is filed as P per project context, but no mintmark is visible in that
frame — stated as a limitation. 007/008 are wide context frames; markers are below their resolution.
009/010 are an opposite-hand pair; the marker zone is visible but small.

## Excluded (not P-mark diagnostic)
- `004_die1-markers-reference.jpg` — reference screenshot, not a coin photo.
- All D-mint files (`takeout-017`–`031`, `015_reverse-d-mint.jpg`, takeout D reverses) — wrong mint.
- `2026-05-06_takeout-026_multi-coin-group-shot.jpg` — group shot, not diagnostic.
- `2026-09-04_takeout-017_microscope-screen-blurry.jpg`, `2026-09-11_takeout-022` (monitor photo),
  `2026-09-08_takeout-021_monitor-closeup-25c-area.jpg` — blurry screen photos, moiré, not diagnostic.
- `2026-09-16_threads-001/002` — carousel cover graphics, not coin photos.
- `takeout-032`–`045` — unexamined takeout images; not assigned P-mark status.

## Open items
- Takeout part 1 (1.98 GB) still pending — may add usable P images when it lands.
- A proper pixel overlay needs a controlled photo set: same camera, same lighting, same orientation,
  no markup. The current archive can't support it.
