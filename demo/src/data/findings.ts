// TL;DR Key Findings - Placeholder numbers for the demo site
// All values are illustrative and pending final results

export interface Finding {
  id: string;
  title: string;
  value: string;
  description: string;
  placeholder: true;
}

export const findings: Finding[] = [
  {
    id: 'speed-accuracy',
    title: 'Speed & Accuracy',
    value: 'No significant improvement',
    description: 'AI suggestions **do not improve** annotation speed or accuracy versus the human-only baseline.',
    placeholder: true,
  },
  {
    id: 'confidence',
    title: 'Self-Reported Confidence',
    value: 'xxx',
    description: 'Annotators reported **higher subjective confidence** when using AI assistance (scale 1–7).',
    placeholder: true,
  },
  {
    id: 'wrong-low',
    title: 'Wrong Acceptance (Low Conf)',
    value: 'xxx',
    description: 'Acceptance rate of **incorrect suggestions** when AI confidence was **low**.',
    placeholder: true,
  },
  {
    id: 'wrong-high',
    title: 'Wrong Acceptance (High Conf)',
    value: 'xxx',
    description: 'Acceptance rate of **incorrect suggestions** when AI confidence was **high** — barely different from low.',
    placeholder: true,
  },
  {
    id: 'scln-random',
    title: 'SCLNScore vs Random',
    value: 'xxx',
    description: 'SCLNScore finds **many more** contaminated labels than random sampling at a fixed review budget.',
    placeholder: true,
  },
  {
    id: 'auprc',
    title: 'AUPRC Improvement',
    value: 'xxx',
    description: 'SCLNScore AUPRC versus **Confident Learning**, the strongest baseline.',
    placeholder: true,
  },
  {
    id: 'cross-dataset',
    title: 'Cross-Dataset Transfer',
    value: 'xxx',
    description: 'SCLNScore AUPRC when **transferring from BDD100K to nuImages** with no retraining.',
    placeholder: true,
  },
];

export const isPlaceholder = true;
