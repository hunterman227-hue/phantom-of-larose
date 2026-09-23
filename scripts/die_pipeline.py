#!/usr/bin/env python3
"""Die-attribution image pipeline for 2026 Mayflower Quarter Audit (Phantom of LaRose).

Stages: gather -> dedupe (dHash) -> ORB medoid clustering -> per-cluster overlays.
Local analysis only. Never deletes source photos.
"""
import os, sys, csv, time, math, random, shutil, pickle
from pathlib import Path
import numpy as np
import cv2
from PIL import Image

random.seed(42); np.random.seed(42)

ROOT = Path('/home/hatch/workspace/your_files/2026-mayflower-quarter-audit-phantom-of-larose')
PHOTOS = ROOT / 'photos'
STAGING = PHOTOS / 'staging_first500'
ANALYSIS = ROOT / 'analysis'
LOG = ANALYSIS / 'pipeline.log'
ANALYSIS.mkdir(exist_ok=True)

MAXDIM = 640
ORB_FEATURES = 1500
LOWE_RATIO = 0.75
GOOD_MIN = 30
INLIER_MIN = 18
DHAMM_MAX = 8
IMG_EXTS = {'.jpg', '.jpeg', '.png', '.heic', '.webp'}
BUDGET_S = 85 * 60  # stop clustering new images after this
RELAY_AFTER = 50    # medoid re-pick cadence

t0 = time.time()
logf = open(LOG, 'a')
def log(msg):
    line = f"[{time.time()-t0:8.1f}s] {msg}"
    print(line, flush=True)
    logf.write(line + '\n'); logf.flush()

# ---------------- gather ----------------
def gather():
    paths = []
    for p in STAGING.rglob('*'):
        if p.is_file() and p.suffix.lower() in IMG_EXTS and p.name != '_count.txt':
            paths.append(p)
    for p in PHOTOS.iterdir():
        if p.is_file() and p.suffix.lower() in IMG_EXTS \
           and p.name != 'contact-sheet-all-45.jpg' \
           and not any(t in p.name for t in ('_composite', '_overlay', '_diffmap', '_grid', '_median')):
            paths.append(p)
    paths = sorted(set(paths))
    log(f"GATHER: {len(paths)} image files (staging + filed)")
    return paths

def load_small(p):
    """Return grayscale image, max dim MAXDIM, or None on failure."""
    try:
        with Image.open(p) as im:
            im = im.convert('L')
            w, h = im.size
            s = MAXDIM / max(w, h)
            if s < 1.0:
                im = im.resize((int(w * s), int(h * s)), Image.LANCZOS)
            return np.asarray(im)
    except Exception as e:
        log(f"  READ FAIL {p.name}: {e}")
        return None

def dhash(g):
    h, w = g.shape
    small = cv2.resize(g, (17, 16), interpolation=cv2.INTER_AREA)
    diff = small[:, 1:] > small[:, :-1]
    return diff.flatten()

def rel(p):
    return str(p.relative_to(ROOT))

# ---------------- dedupe ----------------
def dedupe(paths):
    uniq, hashes, sizes, dupes = [], [], [], []
    unreadable = 0
    for i, p in enumerate(paths):
        if i % 100 == 0:
            log(f"  dedupe {i}/{len(paths)}")
        g = load_small(p)
        if g is None:
            unreadable += 1
            continue
        h = dhash(g)
        sz = p.stat().st_size
        best, bestd = -1, 10 ** 9
        for j, kh in enumerate(hashes):
            d = int(np.count_nonzero(h != kh))
            if d < bestd:
                bestd, best = d, j
                if d == 0:
                    break
        if bestd <= DHAMM_MAX:
            keep_p = uniq[best]
            if sz > sizes[best]:
                dupes.append((rel(p), rel(keep_p), bestd, 'replaced-by-larger'))
                hashes[best] = h; uniq[best] = p; sizes[best] = sz
            else:
                dupes.append((rel(keep_p), rel(p), bestd, 'dropped-smaller'))
        else:
            uniq.append(p); hashes.append(h); sizes.append(sz)
    with open(ANALYSIS / 'dedupe_log.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['kept_file', 'dropped_file', 'hamming', 'note'])
        w.writerows(dupes)
    log(f"DEDUPE: {len(uniq)} unique of {len(paths)} ({len(dupes)} near/exact dupes, {unreadable} unreadable)")
    pickle.dump(uniq, open(ANALYSIS / '_unique.pkl', 'wb'))
    return uniq

# ---------------- ORB descriptors ----------------
orb = cv2.ORB_create(nfeatures=ORB_FEATURES)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

def compute_kp_desc(paths):
    """ORB keypoints + descriptors per image; stores (pts, desc) or (None, None)."""
    kd = {}
    fail = 0
    for i, p in enumerate(paths):
        if i % 50 == 0:
            log(f"  ORB {i}/{len(paths)}")
        g = load_small(p)
        if g is None:
            fail += 1
            continue
        kp, d = orb.detectAndCompute(g, None)
        if d is None or len(d) < 4:
            kd[rel(p)] = (None, None)
        else:
            kd[rel(p)] = (np.array([k.pt for k in kp], dtype=np.float32), d)
    pickle.dump(kd, open(ANALYSIS / '_desc.pkl', 'wb'))
    n_none = sum(1 for v in kd.values() if v[1] is None)
    log(f"ORB: {len(kd)} done, {n_none} no usable features, {fail} unreadable")
    return kd

def homography(kpq, dq, kpr, dr):
    """Lowe-ratio match q->r; RANSAC homography. Returns (good, inliers, H|None)."""
    knn = bf.knnMatch(dq, dr, k=2)
    good = []
    for pair in knn:
        if len(pair) < 2:
            continue
        m, n = pair
        if m.distance < LOWE_RATIO * n.distance:
            good.append(m)
    if len(good) < GOOD_MIN:
        return len(good), 0, None
    src = np.float32([kpq[m.queryIdx] for m in good])
    dst = np.float32([kpr[m.trainIdx] for m in good])
    H, mask = cv2.findHomography(src, dst, cv2.RANSAC, 5.0)
    inl = int(mask.sum()) if mask is not None else 0
    return len(good), inl, H

# ---------------- clustering ----------------
def repick_medoid(cl, kd):
    members = cl['members']
    if len(members) < 3:
        return
    cands = [cl['rep']] + random.sample([m for m in members if m != cl['rep']],
                                        min(4, len(members) - 1))
    best, best_score = cl['rep'], -1
    for c in cands:
        others = [m for m in members if m != c]
        samp = random.sample(others, min(8, len(others)))
        kpc, dc = kd[c]
        s = 0
        for m in samp:
            kpm, dm = kd[m]
            _, inl, _ = homography(kpm, dm, kpc, dc)
            s += inl
        score = s / max(len(samp), 1)
        if score > best_score:
            best, best_score = c, score
    if best != cl['rep']:
        log(f"  medoid {cl['id']}: rep -> {Path(best).name} (score {best_score:.1f})")
        cl['rep'] = best

def cluster(paths, kd):
    clusters = []          # each: id, rep, members[], inliers{member: int}
    unmatched = {'id': 'UNMATCHED', 'rep': None, 'members': [], 'inliers': {}}
    unprocessed = {'id': 'UNPROCESSED', 'rep': None, 'members': [], 'inliers': {}}
    n_new_die = 0
    assigned_since_relay = 0
    stopped_early = False

    for i, p in enumerate(paths):
        rp = rel(p)
        kpq, dq = kd.get(rp, (None, None))
        if i % 25 == 0:
            log(f"  cluster {i}/{len(paths)} ({len(clusters)} dies, unmatched {len(unmatched['members'])})")
        if time.time() - t0 > BUDGET_S:
            log("  BUDGET EXCEEDED: stopping clustering, rest -> UNPROCESSED")
            for q in paths[i:]:
                unprocessed['members'].append(rel(q))
            stopped_early = True
            break
        if dq is None:
            unmatched['members'].append(rp)
            continue
        if not clusters:
            n_new_die += 1
            cid = f'DIE_{n_new_die:02d}'
            clusters.append({'id': cid, 'rep': rp, 'members': [rp], 'inliers': {rp: 0}})
            log(f"  seed die cluster {cid}: {p.name}")
            continue
        best_cl, best_inl, best_good, max_good = None, 0, 0, 0
        for cl in clusters:
            kpr, dr = kd[cl['rep']]
            good, inl, H = homography(kpq, dq, kpr, dr)
            max_good = max(max_good, good)
            if good >= GOOD_MIN and inl >= INLIER_MIN and inl > best_inl:
                best_cl, best_inl, best_good = cl, inl, good
            if good >= 200 and inl >= 100:
                break  # confident early exit
        if best_cl is not None:
            best_cl['members'].append(rp)
            best_cl['inliers'][rp] = best_inl
            assigned_since_relay += 1
        elif max_good < GOOD_MIN:
            unmatched['members'].append(rp)
        else:
            n_new_die += 1
            cid = f'DIE_{n_new_die:02d}'
            clusters.append({'id': cid, 'rep': rp, 'members': [rp], 'inliers': {rp: 0}})
            log(f"  new die cluster {cid}: {p.name}")
            assigned_since_relay += 1
        if assigned_since_relay >= RELAY_AFTER:
            assigned_since_relay = 0
            for cl in clusters:
                repick_medoid(cl, kd)

    allc = clusters + [unmatched] + ([unprocessed] if unprocessed['members'] else [])
    # write clusters.csv
    with open(ANALYSIS / 'clusters.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['cluster_id', 'representative_path', 'member_count', 'mean_inliers', 'member_paths'])
        for cl in allc:
            inl = [v for k, v in cl['inliers'].items() if k != cl['rep']]
            mean_inl = round(sum(inl) / len(inl), 1) if inl else 0
            w.writerow([cl['id'], cl['rep'] or '', len(cl['members']), mean_inl,
                        ';'.join(cl['members'])])
    pickle.dump(allc, open(ANALYSIS / '_clusters.pkl', 'wb'))
    log(f"CLUSTER: {len(clusters)} die clusters, {len(unmatched['members'])} unmatched, "
        f"{len(unprocessed['members'])} unprocessed, early_stop={stopped_early}")
    for cl in clusters:
        log(f"    {cl['id']}: {len(cl['members'])} members rep={Path(cl['rep']).name}")
    return allc, stopped_early

# ---------------- overlays ----------------
def gray(p_rel):
    return load_small(ROOT / p_rel)

def contact_grid(imgs, cols=3, cell=320):
    rows = math.ceil(len(imgs) / cols)
    grid = np.zeros((rows * cell, cols * cell), np.uint8)
    for i, im in enumerate(imgs):
        r, c = divmod(i, cols)
        th = cv2.resize(im, (cell, cell), interpolation=cv2.INTER_AREA)
        grid[r*cell:(r+1)*cell, c*cell:(c+1)*cell] = th
    return grid

def overlays(allc, kd):
    paths_out = []
    aligned_rows = []
    skipped = 0
    for cl in allc:
        cid = cl['id']
        if cid in ('UNMATCHED', 'UNPROCESSED'):
            # thumbnail grid only
            ims = []
            for m in cl['members'][:16]:
                g = gray(m)
                if g is not None:
                    ims.append(g)
            if ims:
                gp = ANALYSIS / f'{cid}_grid.jpg'
                cv2.imwrite(str(gp), cv2.cvtColor(contact_grid(ims, cols=4, cell=300), cv2.COLOR_GRAY2BGR))
                paths_out.append(str(gp))
            continue
        members = cl['members']
        if len(members) == 1:
            sp = ANALYSIS / f'{cid}_single.jpg'
            try:
                shutil.copyfile(ROOT / members[0], sp)
                paths_out.append(str(sp))
            except Exception as e:
                log(f"  singleton copy fail {cid}: {e}"); skipped += 1
            continue
        rep_g = gray(cl['rep'])
        if rep_g is None:
            log(f"  overlay skip {cid}: rep unreadable"); skipped += 1
            continue
        rh, rw = rep_g.shape
        kpr, dr = kd[cl['rep']]
        aligned, ok_members = [rep_g], [cl['rep']]
        aligned_rows.append((cid, cl['rep'], 0, True))
        for m in members:
            if m == cl['rep']:
                continue
            g = gray(m)
            kpm, dm = kd.get(m, (None, None))
            if g is None or dm is None:
                aligned_rows.append((cid, m, 0, False)); skipped += 1
                continue
            good, inl, H = homography(kpm, dm, kpr, dr)
            if H is None or inl < INLIER_MIN:
                aligned_rows.append((cid, m, inl, False)); skipped += 1
                continue
            try:
                wimg = cv2.warpPerspective(g, H, (rw, rh))
                aligned.append(wimg); ok_members.append(m)
                aligned_rows.append((cid, m, inl, True))
            except cv2.error:
                aligned_rows.append((cid, m, inl, False)); skipped += 1
        if len(aligned) < 2:
            log(f"  overlay {cid}: only {len(aligned)} aligned, grid only")
            gp = ANALYSIS / f'{cid}_grid.jpg'
            cv2.imwrite(str(gp), cv2.cvtColor(contact_grid(aligned, cols=3), cv2.COLOR_GRAY2BGR))
            paths_out.append(str(gp))
            continue
        stack = np.stack(aligned).astype(np.float32)
        med = np.median(stack, axis=0).astype(np.uint8)
        mp = ANALYSIS / f'{cid}_median.jpg'
        cv2.imwrite(str(mp), med); paths_out.append(str(mp))
        mad = np.mean(np.abs(stack - med.astype(np.float32)), axis=0)
        mad_n = cv2.normalize(mad, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        dp = ANALYSIS / f'{cid}_diffmap.jpg'
        cv2.imwrite(str(dp), cv2.applyColorMap(mad_n, cv2.COLORMAP_JET))
        paths_out.append(str(dp))
        gp = ANALYSIS / f'{cid}_grid.jpg'
        cv2.imwrite(str(gp), cv2.cvtColor(contact_grid(aligned[:9]), cv2.COLOR_GRAY2BGR))
        paths_out.append(str(gp))
        log(f"  overlay {cid}: {len(aligned)}/{len(members)} aligned -> median/diffmap/grid")
    with open(ANALYSIS / 'aligned_ok.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['cluster_id', 'member_path', 'inliers', 'warped_ok'])
        w.writerows(aligned_rows)
    log(f"OVERLAYS: {len(paths_out)} files written, {skipped} members skipped")
    return paths_out

# ---------------- report ----------------
def report(n_ingest, n_unique, allc, stopped_early, out_paths, extra_notes):
    dies = [c for c in allc if c['id'].startswith('DIE_')]
    unm = next((c for c in allc if c['id'] == 'UNMATCHED'), None)
    unp = next((c for c in allc if c['id'] == 'UNPROCESSED'), None)
    total = time.time() - t0
    lines = [
        "# Die-Attribution Pipeline Report",
        "",
        f"Run finished: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}",
        f"Total wall time: {total/60:.1f} min",
        "",
        "## Parameters",
        f"- max dim 640px, ORB nfeatures={ORB_FEATURES}, Lowe ratio={LOWE_RATIO}",
        f"- assign thresholds: good_matches >= {GOOD_MIN}, homography inliers >= {INLIER_MIN}",
        f"- dedupe: dHash 16x16 (256-bit), hamming <= {DHAMM_MAX}, keep largest file",
        f"- medoid re-pick every {RELAY_AFTER} assignments for clusters >= 3 members",
        f"  (bounded: current rep + up to 4 challengers x up to 8 sampled members)",
        f"- clustering budget: {BUDGET_S/60:.0f} min",
        "",
        "## Counts",
        f"- ingested: {n_ingest}",
        f"- unique after dedupe: {n_unique}",
        f"- die clusters: {len(dies)}",
        f"- unmatched (no cluster, < {GOOD_MIN} good matches to everything): {len(unm['members']) if unm else 0}",
        f"- unprocessed (budget stop): {len(unp['members']) if unp else 0}",
        f"- early stop: {stopped_early}",
        f"- overlay/composite files written: {len(out_paths)}",
        "",
        "## Clusters",
    ]
    for c in dies:
        lines.append(f"- {c['id']}: {len(c['members'])} members, rep={c['rep']}")
    if unm:
        lines.append(f"- UNMATCHED: {len(unm['members'])} members")
    if unp and unp['members']:
        lines.append(f"- UNPROCESSED: {len(unp['members'])} members")
    lines += ["", "## Output files", ""]
    for p in sorted(out_paths):
        lines.append(f"- {Path(p).name}")
    lines += ["", "- clusters: analysis/clusters.csv", "- dedupe log: analysis/dedupe_log.csv",
              "- alignment log: analysis/aligned_ok.csv", "- progress log: analysis/pipeline.log", ""]
    if extra_notes:
        lines += ["## Notes / failures / skips", ""] + [f"- {n}" for n in extra_notes] + [""]
    rp = ROOT / 'notes' / 'PIPELINE_REPORT.md'
    rp.parent.mkdir(exist_ok=True)
    rp.write_text('\n'.join(lines))
    log(f"REPORT written to {rp}")

def main():
    notes = []
    log("=== PIPELINE START ===")
    paths = gather()
    n_ingest = len(paths)
    if not paths:
        log("nothing to do"); return
    uniq = dedupe(paths)
    kd = compute_kp_desc(uniq)
    allc, stopped = cluster(uniq, kd)
    out_paths = overlays(allc, kd)
    # honest quality note: computed stats
    dies = [c for c in allc if c['id'].startswith('DIE_')]
    multi = [c for c in dies if len(c['members']) >= 2]
    if multi:
        inl_means = []
        for c in multi:
            v = [x for k, x in c['inliers'].items() if k != c['rep']]
            if v: inl_means.append(sum(v)/len(v))
        notes.append(f"mean homography inliers across multi-member clusters: "
                     f"{(sum(inl_means)/len(inl_means)):.0f} (assign threshold was {INLIER_MIN})")
    notes.append("dedupe dropped near-duplicates (hamming<=8); check dedupe_log.csv before treating counts as final")
    notes.append("UNMATCHED holds images with no die match: screenshots, fingers, blurry junk, or truly unique views")
    report(n_ingest, len(uniq), allc, stopped, out_paths, notes)
    log("=== PIPELINE DONE ===")
    logf.close()

if __name__ == '__main__':
    main()
