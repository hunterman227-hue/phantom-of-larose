# Die Attribution Report — "First 500" Album + Study Coins
Date: 2026-09-16 (analysis run 2026-09-17 UTC)
Album: "First 500" (Shared, dated Aug 10–17, 2026) — 479 photos downloaded via Google Photos native download
Also cross-referenced: all 45 filed project photos (study coins, takeout, research screenshots)

## Method
1. dHash dedupe: 524 ingested → 466 unique (58 near/exact duplicates logged in `analysis/dedupe_log.csv`)
2. ORB feature matching (1500 features, 640px) with medoid clustering: ≥30 good matches + ≥18 RANSAC inliers required to join a cluster
3. Per-cluster alignment → median composite + JET difference map + member grid, all in `analysis/`
4. Warp-sanity QC: 3 degenerate homographies caught and excluded (DIE_05/08/16)
5. Human visual inspection of composites and member images

Threshold validation: on a 1770-pair sample, true same-view pairs score 100–1500 good matches at ~100% inliers; different coins score <30 with 0 inliers. Wide empty gap — thresholds are sound.

## HEADLINE ANSWER: the album is NOT one working die
The "First 500" album is a multi-day audit shoot (Aug 13–17) of **hundreds of different coins**: full-coin obverses and reverses, macro close-ups, multi-coin group shots, labeled flips (e.g. "Pennsylvania-D", "Delaware-D"), monitor photos, plus non-coin phone screenshots. 420 of 466 unique images matched NOTHING else — each is a distinct coin or a view with no overlapping partner. There is no single working die across this album, so album-wide "same die?" attribution does not apply. What DID group:

## Clusters found (24) — grouped by actual content
### Same-coin photo groups (genuine clusters)
- **DIE_02** (2): consecutive shots 20260815_035901/035908 — same coin, same view
- **DIE_03** (2): 20260815_040913/040921 — same coin, same view
- **DIE_05** (3→2 sane): 20260815_042502/042516 + IMG_0028.PNG — reverse masthead/bowsprit macro; median shows rigging converging at central mast element; diffmap hot zones are lighting/shadow differences between shots, not die features (confidence: low for anomaly purposes — lighting variance dominates)
- **DIE_06** (2): 20260815_042836/042845 — reverse rim "AMERICA" + mast tops close-up; clean normal strike detail, no anomaly visible at composite resolution
- **DIE_08** (3→2 sane): 20260815_042922/042930 + IMG_0114.JPG — same coin macro group
- **DIE_11** (2): 20260816_150054/150058 — weak match (21 inliers), consecutive shots, likely same coin
- **DIE_16** (2→1 sane): 20260816_152047 + a Photos-app screenshot of the same image — same file photographed twice
- **DIE_18** (2): IMG_0054/0055.PNG — identical phone screenshots (lock screen), not coins
### Singletons (one photo, no partner view)
- DIE_01: filed study photo 2025-04-10_phantom-larose-007 (obverse wide) — no First 500 partner found
- DIE_04, 07, 09, 10, 12, 13, 14, 15, 17, 19: single First 500 coin views (obverse portraits, reverse ships, macros)
### Non-coin clusters (flagged, not dies)
- **DIE_20** (6): identical LA OMV website screenshots
- **DIE_21** (3): camp-house architectural drawings (Messenger)
- **DIE_22/23/24**: Facebook + Reddit screenshots (DIE_24 = 6 shots of one Reddit thread)
### UNMATCHED (420)
Distinct coins/views with no overlapping partner, including ALL 44 other filed study-coin photos. Notably: **no filed study-coin photo matched any First 500 photo** — the album contains no additional overlapping views of the Mosquito Bite / Splenter / Phantom study coins that the matcher could find. Caveat: matching needs overlapping views; a full-coin reverse will not match a microscope close-up of the same coin.

## Anomaly check — everything we discussed
Checked across cluster composites, member images, and study-coin photos:
- **Mosquito Bite / Splenter / Ant Bite (Die-1 obverse markers):** present on study-coin filed photos (e.g. 2026-09-13_phantom-larose-001/002/004) per user's own markup. NOT found on any First 500 photo — no First 500 image shows the pilgrim's left-arm/hand region with these markers at visible resolution.
- **Duck Head / Half Phantom / Full Phantom (reverse, front of mast):** study-coin reverses show the progression per user's markup. First 500 reverses inspected at composite resolution show normal mast/sail detail; no phantom-stage chips identified. DIE_05's masthead macro shows normal rigging convergence.
- **Two marks in front of mast + intersection:** not identified on First 500 reverses at available resolution.
- **Elbow / bonnet / face cracks:** no crack features identified on First 500 obverses; study-coin obverse close-ups carry the user's own red-markup annotations (not treated as coin features).
- **Clash, PIDT/transfer, strikethrough, off-center:** none identified in the First 500 set at composite resolution. One group-shot flip labeled flips normally.
- **Chips, cracks, flow lines, deterioration:** nothing flagged beyond normal strike texture; diffmap hot zones in clusters track lighting/shadow differences between handheld shots, NOT die features (do not read these as anomalies).

## Flags
1. **Album ≠ one die.** Anyone treating "First 500" as a single-die population will get nonsense — it's ~500 different coins.
2. **Non-coin images** in the album: phone screenshots, LA OMV site, camp-house drawings, Reddit/Facebook threads (clusters DIE_18/20/21/22/23/24).
3. **Dedupe is approximate:** a few pixel-identical re-filings under different names slipped past dHash (e.g. takeout-017 vs takeout-033 match at 1284/1284 inliers) — "466 unique" is approximate.
4. **Study-coin die linkage:** the 45 filed photos could not be computationally linked into shared-die groups — they're different angles/scales of (mostly) different coins. True die attribution of the study coins needs same-view, same-magnification photo sets.

## Files
- Composites: `analysis/DIE_*_{median,diffmap,grid,single}.jpg`, `analysis/UNMATCHED_grid.jpg`
- `analysis/clusters.csv`, `analysis/aligned_ok.csv`, `analysis/dedupe_log.csv`, `analysis/pipeline.log`
- Full pipeline notes: `notes/PIPELINE_REPORT.md`
- Photos filed: `photos/first500/` (479 images), indexed in `index.csv`
