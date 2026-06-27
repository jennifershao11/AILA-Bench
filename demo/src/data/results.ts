// RQ1–RQ3 & RQ5: main benchmark exports. RQ4: feature ablation (paper appendix).

export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    color: string;
  }[];
  placeholder: boolean;
}

export const studyStats = {
  pilot: 'BDD100K pilot',
  tasksPerCondition: 100_000,
  labelsByCondition: {
    human_only: 837_153,
    ai_assisted: 903_455,
    ai_assisted_confidence: 903_455,
  },
  aurocScln: 0.648,
  auprcScln: 0.469,
  auprcRandomBaseline: 0.317,
};

export const rq1Data = {
  title: 'RQ1: Error Modes',
  question: 'Do AI-assisted annotation errors differ from Human-only errors?',
  pilotNote:
    'BDD100K pilot (Table tab:rq1a). Task-level review_time_ms is logged in interaction traces; it is omitted from this summary table.',
  answer:
    'Overall FDER is similar across conditions (**32.9%** AI-assisted vs **31.5%** human-only), but the **error mix shifts**: AI-assisted labels carry far more **bbox errors (13.9% vs 3.9%)** and fewer **misses (0.3% vs 11.6%)**; false-positive rates stay near **10–12%**.',
  overallFder: {
    labels: ['Human-only', 'AI-assisted', 'AI + Confidence'],
    values: [31.5, 32.9, 30.8],
  },
  accuracy: [68.5, 67.1, 69.2],
  conditions: [
    {
      key: 'human_only',
      tasks: 100_000,
      labels: 837_153,
      accuracy: 68.5,
      fder: 31.5,
      bbox: 3.9,
      class: 0.7,
      fp: 12.2,
      miss: 11.6,
      other: 2.9,
    },
    {
      key: 'ai_assisted',
      tasks: 100_000,
      labels: 903_455,
      accuracy: 67.1,
      fder: 32.9,
      bbox: 13.9,
      class: 3.8,
      fp: 10.1,
      miss: 0.3,
      other: 4.8,
    },
    {
      key: 'ai_assisted_confidence',
      tasks: 100_000,
      labels: 903_455,
      accuracy: 69.2,
      fder: 30.8,
      bbox: 11.5,
      class: 4.1,
      fp: 10.0,
      miss: 0.2,
      other: 5.0,
    },
  ],
  fderByCondition: {
    labels: ['BBox', 'Class', 'FP', 'Miss', 'Other'],
    humanOnly: [3.9, 0.7, 12.2, 11.6, 2.9],
    aiAssisted: [13.9, 3.8, 10.1, 0.3, 4.8],
    aiAssistedConf: [11.5, 4.1, 10.0, 0.2, 5.0],
  },
  placeholder: false,
};

export const rq2Data = {
  title: 'RQ2: AI Error Inheritance',
  question: 'When AI gives a wrong suggestion, do humans inherit the same error — especially at high confidence?',
  answer:
    'Among source-linked final labels, same-error inheritance rises from **66.4%** (AI conf 0.25–0.50) to **87.5%** (conf 0.75–1.00). High-confidence buckets have fewer wrong AI suggestions (**6.0%** vs **43.3%**), but when AI is wrong, inheritance is highest.',
  byConfidence: [
    {
      bucket: '0.25–0.50',
      aiLinkedLabels: 97_097,
      aiWrongRate: 43.3,
      sameErrorInherited: 66.4,
      finalErrorRate: 38.9,
    },
    {
      bucket: '0.50–0.75',
      aiLinkedLabels: 197_318,
      aiWrongRate: 18.9,
      sameErrorInherited: 72.6,
      finalErrorRate: 21.8,
    },
    {
      bucket: '0.75–1.00',
      aiLinkedLabels: 273_548,
      aiWrongRate: 6.0,
      sameErrorInherited: 87.5,
      finalErrorRate: 7.8,
    },
  ],
  inheritanceByConfidence: {
    labels: ['0.25–0.50', '0.50–0.75', '0.75–1.00'],
    sameErrorInherited: [66.4, 72.6, 87.5],
    aiWrongRate: [43.3, 18.9, 6.0],
  },
  summary: {
    aiLinkedLabels: 567_963,
  },
  placeholder: false,
};

export interface ReviewPolicyRow {
  name: string;
  auprc: number | null;
  precisionAt1: number;
  precisionAt5: number;
  recallAt5: number;
  recallAt10: number;
  recallAt20: number;
}

export const rq3Data = {
  title: 'RQ3: SCLNScore vs Review Strategies',
  question: 'Under a limited review budget, does SCLNScore beat traditional re-review strategies?',
  scorerNote:
    'SCLNScore is the trained ranking model used for review prioritization on the full benchmark export. These metrics are **not** the appendix logistic-regression ablation in RQ4.',
  answer:
    'SCLNScore reaches **AUPRC 0.469** (AUROC **0.648**). At **P@5%** it scores **59.5%** vs **31.7%** random — while **high-confidence review collapses** (P@1% **2.1%**). SCLNScore is the best deployable policy in the pilot comparison.',
  sclnMetrics: {
    auroc: studyStats.aurocScln,
    auprc: studyStats.auprcScln,
    randomAuprcBaseline: studyStats.auprcRandomBaseline,
  },
  policies: [
    {
      name: 'Random',
      auprc: null,
      precisionAt1: 0.314,
      precisionAt5: 0.317,
      recallAt5: 0.05,
      recallAt10: 0.1,
      recallAt20: 0.2,
    },
    {
      name: 'Low-confidence',
      auprc: null,
      precisionAt1: 0.325,
      precisionAt5: 0.321,
      recallAt5: 0.05,
      recallAt10: 0.101,
      recallAt20: 0.2,
    },
    {
      name: 'High-confidence',
      auprc: null,
      precisionAt1: 0.021,
      precisionAt5: 0.043,
      recallAt5: 0.007,
      recallAt10: 0.023,
      recallAt20: 0.073,
    },
    {
      name: 'Ensemble',
      auprc: null,
      precisionAt1: 0.679,
      precisionAt5: 0.573,
      recallAt5: 0.09,
      recallAt10: 0.159,
      recallAt20: 0.277,
    },
    {
      name: 'SCLNScore',
      auprc: studyStats.auprcScln,
      precisionAt1: 0.734,
      precisionAt5: 0.595,
      recallAt5: 0.094,
      recallAt10: 0.175,
      recallAt20: 0.32,
    },
  ] satisfies ReviewPolicyRow[],
  placeholder: false,
};

export interface RQ4FeatureGroup {
  name: string;
  featureCount: number;
  auroc: number;
  auprc: number;
  precisionAt1: number;
  recallAt10: number;
  auprcDrop: number;
}

export interface RQ4TopFeature {
  name: string;
  group: string;
  auroc: number;
  auprc: number;
  lift: number;
}

export interface RQ4TraceMean {
  feature: string;
  humanOnly: number;
  aiAssisted: number;
  aiConf: number;
}

export const rq4Data = {
  title: 'RQ4: Feature Importance (Ablation)',
  question: 'Which factors matter most for ranking final-label error risk?',
  appendixNote:
    'Appendix ablation only: class-balanced logistic regression on 17 grouped features, with an image-level train/test split. This is a **separate model** from the SCLNScore ranker in RQ3 — higher AUPRC here reflects a different evaluator and held-out split, not a better deployable ranker.',
  modelLabel: 'Class-balanced logistic regression (full 17 features)',
  answer:
    'The full model reaches **AUPRC 0.678** (AUROC **0.781**), well above the **0.320** random baseline. **Object** is the strongest group (group-only AUPRC **0.566**; removing it drops AUPRC by **0.112**). **AI** features rank second (AUPRC **0.522**, drop **0.083**). **Trace** and **Interface+Time** add weaker but useful signals; **category** is the top single feature (AUPRC **0.507**, lift **1.586**).',
  labels: 272_888,
  testLabels: 54_820,
  testErrorRate: 31.97,
  featureCount: 17,
  fullModel: { auroc: 0.781, auprc: 0.678 },
  randomAuprcBaseline: 0.32,
  groups: [
    {
      name: 'Object',
      featureCount: 2,
      auroc: 0.704,
      auprc: 0.566,
      precisionAt1: 0.642,
      recallAt10: 0.188,
      auprcDrop: 0.112,
    },
    {
      name: 'AI',
      featureCount: 6,
      auroc: 0.682,
      auprc: 0.522,
      precisionAt1: 0.611,
      recallAt10: 0.171,
      auprcDrop: 0.083,
    },
    {
      name: 'Trace',
      featureCount: 6,
      auroc: 0.625,
      auprc: 0.431,
      precisionAt1: 0.487,
      recallAt10: 0.139,
      auprcDrop: 0.031,
    },
    {
      name: 'Interface+Time',
      featureCount: 2,
      auroc: 0.594,
      auprc: 0.397,
      precisionAt1: 0.433,
      recallAt10: 0.126,
      auprcDrop: 0.018,
    },
    {
      name: 'Scene',
      featureCount: 1,
      auroc: 0.558,
      auprc: 0.358,
      precisionAt1: 0.382,
      recallAt10: 0.113,
      auprcDrop: 0.009,
    },
  ] satisfies RQ4FeatureGroup[],
  topFeatures: [
    { name: 'category', group: 'Object', auroc: 0.674, auprc: 0.507, lift: 1.586 },
    { name: 'source_ai_confidence', group: 'AI', auroc: 0.651, auprc: 0.463, lift: 1.448 },
    { name: 'source_ai_error_type', group: 'AI', auroc: 0.631, auprc: 0.436, lift: 1.364 },
    { name: 'source_ai_conf_bucket', group: 'AI', auroc: 0.626, auprc: 0.421, lift: 1.317 },
    { name: 'ai_error_count', group: 'AI', auroc: 0.612, auprc: 0.41, lift: 1.282 },
    { name: 'event_count', group: 'Trace', auroc: 0.604, auprc: 0.397, lift: 1.242 },
    { name: 'review_time_ms', group: 'Interface+Time', auroc: 0.589, auprc: 0.384, lift: 1.201 },
    { name: 'final_area', group: 'Object', auroc: 0.573, auprc: 0.371, lift: 1.16 },
  ] satisfies RQ4TopFeature[],
  traceMeans: [
    { feature: 'box_create', humanOnly: 9.8, aiAssisted: 3.95, aiConf: 3.61 },
    { feature: 'box_edit', humanOnly: 2.15, aiAssisted: 5.88, aiConf: 5.12 },
    { feature: 'box_delete', humanOnly: 0.44, aiAssisted: 1.09, aiConf: 0.96 },
    { feature: 'class_change', humanOnly: 0.21, aiAssisted: 0.39, aiConf: 0.34 },
    { feature: 'confirm', humanOnly: 0.73, aiAssisted: 1.62, aiConf: 1.48 },
  ] satisfies RQ4TraceMean[],
  placeholder: false,
};

export interface TransferMetric {
  label: string;
  bddInDomain: number;
  bddToNuImages: number;
  /** When true, values are error rates in percent (e.g. 31.8). */
  isPercent?: boolean;
}

export const rq5Data = {
  title: 'RQ5: Cross-Dataset Transfer',
  question: 'Can SCLNScore trained on BDD100K transfer to other datasets?',
  answer:
    'After transfer to nuImages, ranking metrics decrease: AUROC **0.665 → 0.607**, AUPRC **0.472 → 0.418**, R@10% **0.174 → 0.126**. nuImages error rate is **30.8%** (random AUPRC baseline); transferred AUPRC **0.418** is **11.0 pp above** that baseline — without retraining, SCLNScore still ranks erroneous labels ahead of random review.',
  nuImagesImages: 9_752,
  metrics: [
    { label: 'Err. rate', bddInDomain: 31.8, bddToNuImages: 30.8, isPercent: true },
    { label: 'AUROC', bddInDomain: 0.665, bddToNuImages: 0.607 },
    { label: 'AUPRC', bddInDomain: 0.472, bddToNuImages: 0.418 },
    { label: 'R@10%', bddInDomain: 0.174, bddToNuImages: 0.126 },
  ] satisfies TransferMetric[],
  placeholder: false,
};

export const benchmarkStats = {
  annotators: 370,
  images: 100_000,
  conditions: 3,
  numClasses: 8,
  traceFields: [
    'action_type',
    'review_time_ms',
    'bbox_edit_distance',
    'ai_final_iou',
    'ai_confidence',
    'class_change',
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
  placeholder: false,
};

export const isPlaceholder = false;
