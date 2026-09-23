# Die-Attribution Pipeline Report

Run finished: 2026-09-17 03:06:00 UTC
Total wall time: 2.6 min

## Parameters
- max dim 640px, ORB nfeatures=1500, Lowe ratio=0.75
- assign thresholds: good_matches >= 30, homography inliers >= 18
- dedupe: dHash 16x16 (256-bit), hamming <= 8, keep largest file
- medoid re-pick every 50 assignments for clusters >= 3 members
  (bounded: current rep + up to 4 challengers x up to 8 sampled members)
- clustering budget: 85 min

## Counts
- ingested: 524
- unique after dedupe: 466
- die clusters: 24
- unmatched (no cluster, < 30 good matches to everything): 420
- unprocessed (budget stop): 0
- early stop: False
- overlay/composite files written: 45 (after QC cleanup)

## Clusters
- DIE_01: 1 members, rep=photos/2025-04-10_phantom-larose-007_wide-231851.jpg
- DIE_02: 2 members, rep=photos/staging_first500/First 500/20260815_035901.jpg
- DIE_03: 2 members, rep=photos/staging_first500/First 500/20260815_040913.jpg
- DIE_04: 1 members, rep=photos/staging_first500/First 500/20260815_041147.jpg
- DIE_05: 3 members, rep=photos/staging_first500/First 500/20260815_042502.jpg
- DIE_06: 2 members, rep=photos/staging_first500/First 500/20260815_042836.jpg
- DIE_07: 1 members, rep=photos/staging_first500/First 500/20260815_042909.jpg
- DIE_08: 3 members, rep=photos/staging_first500/First 500/20260815_042922.jpg
- DIE_09: 1 members, rep=photos/staging_first500/First 500/20260815_043004.jpg
- DIE_10: 1 members, rep=photos/staging_first500/First 500/20260816_145910.jpg
- DIE_11: 2 members, rep=photos/staging_first500/First 500/20260816_150054.jpg
- DIE_12: 1 members, rep=photos/staging_first500/First 500/20260816_150102.jpg
- DIE_13: 1 members, rep=photos/staging_first500/First 500/20260816_150107.jpg
- DIE_14: 1 members, rep=photos/staging_first500/First 500/20260816_150114.jpg
- DIE_15: 1 members, rep=photos/staging_first500/First 500/20260816_150144.jpg
- DIE_16: 2 members, rep=photos/staging_first500/First 500/20260816_152047.jpg
- DIE_17: 1 members, rep=photos/staging_first500/First 500/IMG_0053.PNG
- DIE_18: 2 members, rep=photos/staging_first500/First 500/IMG_0054.PNG
- DIE_19: 1 members, rep=photos/staging_first500/First 500/IMG_0092.JPG
- DIE_20: 6 members, rep=photos/staging_first500/First 500/IMG_0105.PNG
- DIE_21: 3 members, rep=photos/staging_first500/First 500/Messenger_creation_38540D8A-CE28-484A-B0B0-C946B218C6F8.jpeg
- DIE_22: 1 members, rep=photos/staging_first500/First 500/Screenshot_20260813_132046_Facebook.jpg
- DIE_23: 1 members, rep=photos/staging_first500/First 500/Screenshot_20260815_091649_Reddit.jpg
- DIE_24: 6 members, rep=photos/staging_first500/First 500/Screenshot_20260815_094304_Reddit.jpg
- UNMATCHED: 420 members

## Output files

- DIE_01_single.jpg
- DIE_02_diffmap.jpg
- DIE_02_grid.jpg
- DIE_02_median.jpg
- DIE_03_diffmap.jpg
- DIE_03_grid.jpg
- DIE_03_median.jpg
- DIE_04_single.jpg
- DIE_05_diffmap.jpg
- DIE_05_grid.jpg
- DIE_05_median.jpg
- DIE_06_diffmap.jpg
- DIE_06_grid.jpg
- DIE_06_median.jpg
- DIE_07_single.jpg
- DIE_08_diffmap.jpg
- DIE_08_grid.jpg
- DIE_08_median.jpg
- DIE_09_single.jpg
- DIE_10_single.jpg
- DIE_11_diffmap.jpg
- DIE_11_grid.jpg
- DIE_11_median.jpg
- DIE_12_single.jpg
- DIE_13_single.jpg
- DIE_14_single.jpg
- DIE_15_single.jpg
- DIE_16_diffmap.jpg
- DIE_16_grid.jpg
- DIE_16_median.jpg
- DIE_17_single.jpg
- DIE_18_diffmap.jpg
- DIE_18_grid.jpg
- DIE_18_median.jpg
- DIE_19_single.jpg
- DIE_20_diffmap.jpg
- DIE_20_grid.jpg
- DIE_20_median.jpg
- DIE_21_diffmap.jpg
- DIE_21_grid.jpg
- DIE_21_median.jpg
- DIE_22_single.jpg
- DIE_23_single.jpg
- DIE_24_diffmap.jpg
- DIE_24_grid.jpg
- DIE_24_median.jpg
- UNMATCHED_grid.jpg

- clusters: analysis/clusters.csv
- dedupe log: analysis/dedupe_log.csv
- alignment log: analysis/aligned_ok.csv
- progress log: analysis/pipeline.log

## Notes / failures / skips

- mean homography inliers across multi-member clusters: 143 (assign threshold was 18)
- dedupe dropped near-duplicates (hamming<=8); check dedupe_log.csv before treating counts as final
- UNMATCHED holds images with no die match: screenshots, fingers, blurry junk, or truly unique views

## Post-run QC (warp sanity check)
- Re-verified every multi-member cluster: warped each member's corners through its
  homography and compared the warped quad area to the representative canvas.
  Members with collapsed/extreme warps (area ratio < 0.2 or > 5.0) were excluded
  and their median/diffmap/grid composites regenerated.
- 3 degenerate warps excluded:
  - DIE_05 / IMG_0028.PNG (good=43, inl=24, area_ratio=0.00)
  - DIE_08 / IMG_0114.JPG (good=33, inl=20, area_ratio=0.00)
  - DIE_16 / Screenshot_20260815_102200_Photos.jpg (good=52, inl=39, area_ratio=0.00)
- DIE_16 dropped to 1 sane member: contaminated median/diffmap deleted, grid
  rewritten as the representative alone (treated as singleton).
- Cause: RANSAC can pass the inlier threshold on repetitive linear structures
  (ship rigging) yet return a near-degenerate transform. Inlier count alone did
  not catch these; the corner-area check did.
- Per-member warp results (incl. good/inlier counts and area ratios) are in
  analysis/aligned_ok.csv (warped_ok column; note column explains exclusions).

## Honest cluster-quality assessment
- Clusters are CLEAN when images match: true same-view pairs score hundreds to
  1500 good matches with near-100% inliers; different coins/views score <30 good
  with 0 inliers. The 30/18 thresholds sit in a wide empty gap (verified on a
  1770-pair random sample: only 1.2% of pairs reached >=30 good matches, and the
  max was 1191). Threshold choice is not splitting true pairs.
- The 420 UNMATCHED images are not a matching failure: the "First 500" album is
  an audit of ~500 different coins (plus screenshots, group shots, fingers,
  monitor photos). Most photos genuinely show distinct coins with no overlapping
  view, so they cannot and should not cluster.
- Limitation: photos of the SAME coin at very different angles/scales (wide shot
  vs tight macro of a different area) do not match - die attribution needs
  overlapping views. Also obverse and reverse of one coin never match each other
  (different dies by definition); cross-side linking must be done by filename/
  capture sequence, not by image matching.
- Note: several "clusters" are not coins at all (e.g. DIE_20 = 6 identical
  Louisiana OMV website screenshots; DIE_22/23/24 = Facebook/Reddit screenshots).
  They clustered correctly as identical images; the DIE_ label is just a label.
- Duplicate hygiene: dedupe dropped 58 near/exact dupes (dedupe_log.csv), but a
  few pixel-identical images filed under different names survived it (e.g.
  2026-09-04_takeout-017 vs takeout-033_20260904_150258.jpg match at 1284/1284
  inliers yet their dHash hamming exceeded 8). Counts of "unique" images should
  be treated as approximate until that log is reviewed.
- No source photos were deleted or modified. index.csv was not touched.
