// RQ1-RQ5 Results - Placeholder metrics for the demo site
// All values are illustrative and pending final results.
// RQ definitions follow the paper:
//   RQ1 error modes, RQ2 high-confidence acceptance, RQ3 SCLNScore vs review
//   strategies, RQ4 feature-importance ablation, RQ5 cross-dataset transfer.

export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    color: string;
  }[];
  placeholder: true;
}

// RQ1: Are AI-assisted annotation errors different from Human-only errors?
export const rq1Data = {
  title: 'RQ1: Error Modes',
  question: 'Do AI-assisted annotation errors differ from Human-only errors?',
  answer:
    'AI assistance **does not reduce the overall final error rate**, but it **reshapes the error profile**: annotators tend to **preserve the AI box-localization and class errors** instead of producing independent human mistakes.',
  // Final Detection Error Rate breakdown by condition (%)
  fderByCondition: {
    labels: ['FDER-box', 'FDER-class', 'FDER-miss', 'FDER-fp', 'FDER-dup'],
    humanOnly: [9, 5, 8, 2, 1],
    aiAssisted: [11, 8, 5, 4, 3],
    aiAssistedConf: [11, 9, 5, 4, 3],
  },
  placeholder: true,
};

// RQ2: Are high-confidence wrong AI suggestions accepted more often?
export const rq2Data = {
  title: 'RQ2: High-Confidence Error Acceptance',
  question: 'Are wrong AI suggestions accepted more often when AI confidence is high?',
  answer:
    'Acceptance of wrong suggestions is **largely insensitive to AI confidence** (about **xxx at low vs xxx at high**), so **high confidence does not keep errors out** — even though annotators report higher subjective confidence (xxx).',
  acceptanceByConfidence: {
    labels: ['Low (bottom 33%)', 'Medium (mid 33%)', 'High (top 33%)'],
    correctAcceptance: [62, 78, 91],
    wrongAcceptance: [55, 60, 64],
  },
  selfReportedConfidence: {
    humanOnly: 4.6,
    aiAssisted: 5.8,
    aiAssistedWithConf: 5.9,
  },
  placeholder: true,
};

// RQ3: Does SCLNScore beat traditional re-review strategies under a budget?
export const rq3Data = {
  title: 'RQ3: SCLNScore vs Review Strategies',
  question: 'Under a limited review budget, does SCLNScore beat traditional re-review strategies?',
  answer:
    'SCLNScore **ranks AI-contaminated labels best** at small budgets, finding about **xxx more than random** review at a fixed budget and reaching **AUPRC xxx vs xxx** for Confident Learning. Confidence-based review is **close to random**.',
  policies: [
    { name: 'Random', auprc: 0.3, recallAt1: 0.012, recallAt5: 0.058, recallAt10: 0.115, recallAt20: 0.22 },
    { name: 'Low-confidence', auprc: 0.31, recallAt1: 0.018, recallAt5: 0.07, recallAt10: 0.13, recallAt20: 0.24 },
    { name: 'High-confidence', auprc: 0.29, recallAt1: 0.014, recallAt5: 0.06, recallAt10: 0.12, recallAt20: 0.225 },
    { name: 'High-loss', auprc: 0.34, recallAt1: 0.03, recallAt5: 0.1, recallAt10: 0.18, recallAt20: 0.3 },
    { name: 'Ensemble disagreement', auprc: 0.33, recallAt1: 0.028, recallAt5: 0.095, recallAt10: 0.175, recallAt20: 0.295 },
    { name: 'Confident Learning', auprc: 0.3, recallAt1: 0.025, recallAt5: 0.09, recallAt10: 0.165, recallAt20: 0.285 },
    { name: 'SCLNScore', auprc: 0.49, recallAt1: 0.12, recallAt5: 0.33, recallAt10: 0.47, recallAt20: 0.64 },
  ],
  placeholder: true,
};

// RQ4: Which factors most affect AI-induced label noise? (feature-group ablation)
export const rq4Data = {
  title: 'RQ4: Feature Importance (Ablation)',
  question: 'Which factors matter most for detecting AI-induced label noise?',
  answer:
    'Removing **human interaction-trace features** causes the **largest drop in AUPRC**, followed by AI confidence / error type and model disagreement. **Human–AI interaction signals are the key** to identifying AI-contaminated labels.',
  ablation: {
    full: 0.49,
    groups: [
      { name: 'w/o Human trace', auprc: 0.34, drop: 0.15 },
      { name: 'w/o AI features', auprc: 0.41, drop: 0.08 },
      { name: 'w/o Object', auprc: 0.45, drop: 0.04 },
      { name: 'w/o Scene', auprc: 0.46, drop: 0.03 },
      { name: 'w/o Interface', auprc: 0.47, drop: 0.02 },
    ],
  },
  placeholder: true,
};

// RQ5: Does SCLNScore trained on BDD100K transfer to other datasets?
export const rq5Data = {
  title: 'RQ5: Cross-Dataset Transfer',
  question: 'Does SCLNScore trained on BDD100K generalize to other datasets?',
  answer:
    'Cross-dataset performance drops versus in-domain but **stays well above baselines**; transferring BDD100K to nuImages **keeps AUPRC at xxx**, and a small amount of **target fine-tuning recovers most of the gap**.',
  transferResults: [
    { source: 'BDD100K', target: 'BDD100K (in-domain)', auprc: 0.49 },
    { source: 'BDD100K', target: 'nuImages (cross-domain)', auprc: 0.38 },
    { source: 'BDD100K', target: 'nuImages (+ fine-tune)', auprc: 0.45 },
    { source: 'BDD100K', target: 'Waymo 2D (cross-domain)', auprc: 0.36 },
  ],
  placeholder: true,
};

// Benchmark overview stats
export const benchmarkStats = {
  annotators: 370,
  images: 100000,
  conditions: 3,
  numClasses: 8,
  traceFields: [
    'action_type',
    'review_time',
    'bbox_edit_distance',
    'ai_final_iou',
    'ai_confidence',
    'class_changed',
    'ai_error_type',
    'final_correctness',
  ],
  classes: [
    'car',
    'pedestrian',
    'rider',
    'bus',
    'truck',
    'motorcycle',
    'traffic light',
    'traffic sign',
  ],
  placeholder: true,
};

export const isPlaceholder = true;
