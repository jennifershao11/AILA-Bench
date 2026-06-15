// Real demo scene: a BDD100K frame with its actual YOLO11 pre-annotations.
// Boxes and confidences are the real model outputs from
// outputs/bdd100k/yolo11_predictions.jsonl (image_external_id 0000f77c-6257be58).
// Unlike the placeholder metrics, these are genuine AI suggestions.

export interface SceneBox {
  id: number;
  category: string;
  confidence: number;
  // [x, y, width, height] in image pixel coordinates
  bbox: [number, number, number, number];
}

export const demoScene = {
  source: 'BDD100K',
  externalId: '0000f77c-6257be58',
  imagePath: '/demo-assets/0000f77c-6257be58.jpg',
  width: 1280,
  height: 720,
  model: 'YOLO11',
  // Real YOLO11 detections for this frame.
  boxes: [
    { id: 1, category: 'car', confidence: 0.913, bbox: [59.3, 251.8, 304.5, 236.1] },
    { id: 2, category: 'car', confidence: 0.788, bbox: [504.7, 224.8, 405.7, 215.6] },
    { id: 3, category: 'traffic light', confidence: 0.772, bbox: [1125.4, 137.8, 35.9, 72.3] },
    { id: 4, category: 'traffic light', confidence: 0.645, bbox: [1164.3, 137.9, 31.9, 70.9] },
    { id: 5, category: 'car', confidence: 0.482, bbox: [4.9, 560.7, 1268.6, 151.1] },
  ] as SceneBox[],
};

// Color per class (shared across demo viewer and case gallery).
export const classColors: Record<string, string> = {
  car: '#3b82f6',
  pedestrian: '#ef4444',
  rider: '#f97316',
  bus: '#a855f7',
  truck: '#eab308',
  motorcycle: '#ec4899',
  'traffic light': '#06b6d4',
  'traffic sign': '#22c55e',
  none: '#64748b',
};

export function classColor(category: string): string {
  return classColors[category] ?? '#3b82f6';
}
