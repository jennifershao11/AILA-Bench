# Demo data request — what the server needs to produce

This is everything the demo needs from the server so we can replace placeholder
case images with **real** data. Goal: nothing fabricated is shown as fact.

Source files on the server:
- Images: `data/bdd100k_prepared/bdd100k_images_100k/100k/train/<externalId>.jpg` (native **1280×720**)
- GT labels: `bdd100k_labels/100k/train/<externalId>.json` — `box2d {x1,y1,x2,y2}` + `category` (+ occluded/truncated)
- YOLO11 preds: `outputs/bdd100k/yolo11_predictions.jsonl` — fields: `image_external_id`, `category`, `confidence`, `bbox [x,y,w,h]`, ... (1,967 preds over ~287 images; 332 preds with conf > 0.8)

---

## 1. Coordinate + format conventions (must match exactly)

- All boxes are pixel **`[x, y, width, height]`**, top-left origin, at the image's native resolution.
  - YOLO JSONL already uses `[x, y, w, h]` → use as-is.
  - GT `box2d` is `{x1,y1,x2,y2}` → convert: `[x1, y1, x2 - x1, y2 - y1]`.
- Class names must be one of the **8 benchmark classes**, lowercase, exactly:
  `car`, `pedestrian`, `rider`, `bus`, `truck`, `motorcycle`, `traffic light`, `traffic sign`.
  Map any COCO/YOLO names to these (e.g. `person` → `pedestrian`). Use `none` only where noted.
- `confidence` is a float 0–1 (as in the JSONL).

---

## 2. Deliverables

### (a) Image files
For each selected case, copy the original BDD100K JPG and name it `case-1.jpg … case-N.jpg`
(N up to 8). Put them in a folder I can access; I'll drop them into `demo/public/cases/`.
**Keep them as the original 1280×720 frames** (do not crop/resize/annotate — the demo draws boxes itself).

### (b) Manifest JSON (`cases_manifest.json`)
One object per case. Schema:

```json
{
  "cases": [
    {
      "id": "case-1",
      "errorType": "class",
      "image": { "file": "case-1.jpg", "externalId": "0000f77c-6257be58", "width": 1280, "height": 720 },
      "focus": {
        "gt": { "class": "truck", "bbox": [120.0, 180.0, 200.0, 150.0] },
        "ai": { "class": "car",   "bbox": [124.0, 182.0, 196.0, 148.0], "confidence": 0.91 },
        "iou": 0.86
      },
      "allBoxes": {
        "gt": [ { "class": "truck", "bbox": [120,180,200,150] } ],
        "ai": [ { "class": "car", "bbox": [124,182,196,148], "confidence": 0.91 } ]
      }
    }
  ]
}
```

Field notes:
- `errorType` ∈ `class | localization | hallucination | missing | duplicate | correct` (+ optional `wrong_object`).
- `focus` = the single GT/AI pair that demonstrates the error (what the gallery highlights).
  - For `hallucination` (false positive): `focus.gt = null`.
  - For `missing` (false negative): `focus.ai = null`.
  - `focus.iou` = IoU between `focus.gt` and `focus.ai` (use `0` if one side is null).
- `allBoxes` = **every** GT box and **every** AI box in that frame (preferred — lets the demo render the
  full scene honestly, not just the focal pair). If too costly, send at least the focal boxes.

### (c) Optional: one extra clean frame for the interactive viewer
A second frame where YOLO's predictions are clean/correct, same manifest fields. Nice-to-have, not required.

---

## 3. How to select each error mode (IoU-based mining over the ~287 predicted images)

Run YOLO preds against GT for each image; `IoU` = standard box IoU.

- **#1 class confusion** — AI box & GT box with `IoU ≥ 0.5` but **different** category.
- **#2 localization** — same category, `IoU ∈ [0.3, 0.6)`.
- **#3 hallucination** (false positive) — AI box whose **max IoU over all GT < 0.1**. (`focus.gt = null`)
- **#4 missing** (false negative) — GT box whose **max IoU over all AI < 0.1**. (`focus.ai = null`)
- **#5 duplicate** — two AI boxes, same category, `IoU ≥ 0.7` with each other, over one GT object.
- **#7 correct acceptance** (positive control) — AI & GT same category, `IoU ≥ 0.7`, `confidence ≥ 0.5`.
- **#8 high-confidence error** — any of #1/#2/#3 where the AI box `confidence > 0.8` (332 such preds exist).
- **#6 wrong instance** — *optional / best-effort.* Heuristic is weak; skip if no clean example.

Constraints:
- **Avoid rare classes** where preds are too few to find clean cases: `rider` (1 pred), `traffic sign` (2),
  `motorcycle` (6). Prefer `car`, `truck`, `bus`, `traffic light`.
- **Eyeball each candidate**: open the actual frame and confirm it visually, unmistakably shows that error mode.
  IoU only narrows candidates; final pick should be "obvious at a glance."
- 4–6 strong, clearly-correct cases are better than 8 forced ones.

---

## 4. Do NOT send / not needed (would be fabricated)

The demo will keep these as explicit placeholders until real annotation is collected, so don't invent them:
- `human-final` box (what the annotator ended with)
- human action / outcome (accept / edit / reject / add)
- review time, bbox edit distance, human-final IoU
These require real `ai_assisted` / `ai_assisted_confidence` submissions (currently 0 collected).

---

## 5. Delivery checklist

1. `case-1.jpg … case-N.jpg` (original 1280×720 BDD100K frames).
2. `cases_manifest.json` (schema in §2b).
3. (optional) one extra clean frame + its manifest entry for the viewer.

Hand me the folder; I wire it into `demo/src/data/cases.ts` and `demoScene.ts`
(box format already matches: `[x, y, w, h]` px, same 8 class names).
