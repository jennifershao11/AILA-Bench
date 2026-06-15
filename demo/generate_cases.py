import json, collections, shutil
from pathlib import Path
from PIL import Image as PILImage

ROOT = Path(__file__).resolve().parents[1]          # repo root
LBL  = ROOT/"data/bdd100k_prepared/bdd100k_labels/100k/train"
IMG  = ROOT/"data/bdd100k_prepared/bdd100k_images_100k/100k/train"
PRED = ROOT/"outputs/bdd100k/yolo11_predictions.jsonl"
OUT  = Path(__file__).resolve().parent/"public/cases"; OUT.mkdir(parents=True, exist_ok=True)
TARGET = {"car","pedestrian","rider","bus","truck","motorcycle","traffic light","traffic sign"}


def iou(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    ix1 = max(ax, bx); iy1 = max(ay, by); ix2 = min(ax + aw, bx + bw); iy2 = min(ay + ah, by + bh)
    iw = max(0, ix2 - ix1); ih = max(0, iy2 - iy1); inter = iw * ih
    u = aw * ah + bw * bh - inter
    return round(inter / u, 3) if u > 0 else 0.0


def load_preds():
    preds = collections.defaultdict(list)
    for line in open(PRED):
        d = json.loads(line)
        preds[d["image_external_id"]].append({
            "class": d["category"],
            "bbox": [round(float(v), 1) for v in d["bbox"]],
            "confidence": round(float(d["confidence"]), 3),
        })
    return preds


def gt_of(ext):
    rec = json.load(open(LBL / f"{ext}.json"))
    frames = rec.get("frames")
    objs = frames[0].get("objects", []) if frames else rec.get("labels", [])
    out = []
    for o in objs:
        c = o.get("category"); b = o.get("box2d")
        if c in TARGET and b:
            x1, y1, x2, y2 = float(b["x1"]), float(b["y1"]), float(b["x2"]), float(b["y2"])
            if x2 > x1 and y2 > y1:
                out.append({"class": c, "bbox": [round(x1, 1), round(y1, 1), round(x2 - x1, 1), round(y2 - y1, 1)]})
    return out


def best_pair(gt, ai):
    """Highest-IoU same-class pair (used to auto-pick the viewer focus)."""
    best = (0.0, None, None)
    for g in gt:
        for a in ai:
            if a["class"] == g["class"]:
                v = iou(g["bbox"], a["bbox"])
                if v > best[0]:
                    best = (v, g, a)
    return best


def entry(preds, cid, error_type, ext, focus=None):
    shutil.copy(IMG / f"{ext}.jpg", OUT / f"{cid}.jpg")
    with PILImage.open(IMG / f"{ext}.jpg") as im:
        w, h = im.size
    gt = gt_of(ext)
    ai = preds[ext]
    if focus is None:
        v, g, a = best_pair(gt, ai)
        focus = {
            "gt": {"class": g["class"], "bbox": g["bbox"]},
            "ai": {"class": a["class"], "bbox": a["bbox"], "confidence": a["confidence"]},
            "iou": v,
        }
    else:
        focus["iou"] = iou(focus["gt"]["bbox"], focus["ai"]["bbox"]) if (focus["gt"] and focus["ai"]) else 0.0
    return {
        "id": cid,
        "errorType": error_type,
        "image": {"file": f"{cid}.jpg", "externalId": ext, "width": w, "height": h},
        "focus": focus,
        "allBoxes": {
            "gt": [{"class": g["class"], "bbox": g["bbox"]} for g in gt],
            "ai": [{"class": a["class"], "bbox": a["bbox"], "confidence": a["confidence"]} for a in ai],
        },
    }


def main():
    preds = load_preds()
    cases = [
        entry(preds, "case-1", "correct", "000f8d37-d4c09a0f",
              {"gt": {"class": "car", "bbox": [928.4, 283.8, 351.0, 374.6]},
               "ai": {"class": "car", "bbox": [927.9, 286.3, 351.7, 372.2], "confidence": 0.891}}),
        entry(preds, "case-2", "class", "0062ab5a-54bb129b",
              {"gt": {"class": "car", "bbox": [392.8, 262.5, 288.1, 193.4]},
               "ai": {"class": "truck", "bbox": [389.9, 262.6, 289.0, 191.9], "confidence": 0.771}}),
        entry(preds, "case-3", "localization", "003e23ee-67d25f19",
              {"gt": {"class": "car", "bbox": [1.7, 91.5, 693.4, 489.8]},
               "ai": {"class": "car", "bbox": [0.4, 90.4, 1259.4, 620.7], "confidence": 0.349}}),
        entry(preds, "case-4", "hallucination", "0062e803-38c0a33a",
              {"gt": None,
               "ai": {"class": "bus", "bbox": [944.3, 262.3, 334.7, 344.2], "confidence": 0.609}}),
        entry(preds, "case-5", "missing", "0077ccb8-d5778190",
              {"gt": {"class": "car", "bbox": [941.3, 316.9, 336.5, 271.4]},
               "ai": None}),
    ]
    viewer = entry(preds, "viewer-clean", "correct", "006a4209-286a5664")

    (OUT / "cases_manifest.json").write_text(
        json.dumps({"cases": cases, "viewer": viewer}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(cases)} cases + viewer to {OUT}")


if __name__ == "__main__":
    main()
