// SCLN Case Gallery — real BDD100K frames with real ground-truth and YOLO11 boxes.
//
// Data source: cases_manifest.json (generated on the server by demo/generate_cases.py
// from data/bdd100k_prepared + bdd100k_labels + outputs/bdd100k/yolo11_predictions.jsonl).
// Every image, ground-truth box, AI box, confidence and GT–AI IoU below is REAL.
//
// What is intentionally NOT here (no real data collected yet): the human-final box and
// human interaction metrics (accept/edit/reject, review time, edit distance). Those require
// real ai_assisted / ai_assisted_confidence annotation and are shown as "pending" in the UI.

import manifest from './cases_manifest.json';
import { publicPath } from '../publicPath';

export type AIErrorType =
  | 'class'
  | 'localization'
  | 'hallucination'
  | 'missing'
  | 'duplicate'
  | 'wrong_object'
  | 'correct';

export interface CaseBox {
  class: string;
  // [x, y, width, height] in image pixel coordinates
  bbox: [number, number, number, number];
  confidence?: number;
}

export interface AnnotationCase {
  id: string;
  title: string;
  description: string;
  imagePath: string;
  externalId: string;
  width: number;
  height: number;
  errorType: AIErrorType;
  focus: { gt: CaseBox | null; ai: CaseBox | null; iou: number };
  allBoxes: { gt: CaseBox[]; ai: CaseBox[] };
}

interface ManifestEntry {
  id: string;
  errorType: string;
  image: { file: string; externalId: string; width: number; height: number };
  focus: { gt: CaseBox | null; ai: CaseBox | null; iou: number };
  allBoxes: { gt: CaseBox[]; ai: CaseBox[] };
}

// Hand-written copy per case. Strictly describes the model output and the task the
// annotator faces — never a recorded human action (we have none yet).
const copy: Record<string, { title: string; description: string }> = {
  'case-1': {
    title: 'Correct suggestion',
    description:
      'YOLO11 proposes this car with high confidence and near-perfect overlap with ground truth. A correct suggestion the annotator should simply accept — our positive control.',
  },
  'case-2': {
    title: 'Class confusion',
    description:
      'The box is well-placed, but YOLO11 labels this car as a truck. A plausible-looking wrong class is exactly the kind of error that tends to slip through review.',
  },
  'case-3': {
    title: 'Localization error',
    description:
      'Right class, wrong extent: the suggested car box is far larger than the true object (low GT–AI IoU). The annotator would need to resize it.',
  },
  'case-4': {
    title: 'Hallucination',
    description:
      'YOLO11 proposes a bus where ground truth has no such object — a false positive the annotator must reject.',
  },
  'case-5': {
    title: 'Missing object',
    description:
      'A real car in ground truth that YOLO11 did not detect. With no suggestion to react to, the annotator has to add it from scratch.',
  },
};

function build(entry: ManifestEntry): AnnotationCase {
  const c = copy[entry.id] ?? { title: entry.id, description: '' };
  return {
    id: entry.id,
    title: c.title,
    description: c.description,
    imagePath: publicPath(`cases/${entry.image.file}`),
    externalId: entry.image.externalId,
    width: entry.image.width,
    height: entry.image.height,
    errorType: entry.errorType as AIErrorType,
    focus: entry.focus,
    allBoxes: entry.allBoxes,
  };
}

export const cases: AnnotationCase[] = (manifest.cases as unknown as ManifestEntry[]).map(build);

// Optional clean frame available for the interactive viewer (real GT + YOLO11 boxes).
export const viewerCase: AnnotationCase = build(manifest.viewer as unknown as ManifestEntry);
