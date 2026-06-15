# 人工实验运行手册

## 研究者准备

1. 确认 BDD100K pilot 数据、任务和 YOLO11 参考框已经准备好。

```bash
python -m experiments.prepare_bdd100k --source-dir data/bdd100k_official --output-dir data/bdd100k_prepared --extract
python -m experiments.import_bdd100k --config configs/default.yaml --bdd-labels data/bdd100k_prepared/bdd100k_labels/100k/train --image-root data/bdd100k_prepared/bdd100k_images_100k/100k/train --limit 300 --reset-db
python -m experiments.create_tasks --config configs/default.yaml
python -m experiments.yolo11_pipeline --config configs/default.yaml --dataset bdd100k --split pilot --limit 300 --weights models/yolo11n.pt --output outputs/bdd100k/yolo11_predictions.jsonl
python -m experiments.import_suggestions --config configs/default.yaml --input outputs/bdd100k/yolo11_predictions.jsonl
```

2. 如果需要清空已有人工提交并重新开放所有任务：

```bash
python -m experiments.reset_annotations --config configs/default.yaml
```

3. 启动服务。

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8001
```

```bash
cd frontend
npm run dev -- --host 0.0.0.0 --port 5174
```

## 标注员说明

访问 `http://<server-ip>:5174`，停留在“标注”页，输入分配的参与者编号，然后点击“开始下一张”。

每张图需要完成：

- 标出目标类别列表中的所有可见目标。
- 如果界面出现参考框，逐一检查、修正或删除。
- 如果界面没有参考框，直接从原图绘制目标框。
- 只使用界面右侧显示的 8 个目标类别。
- 确认本图完整后点击“提交本图”。

不要向参与者说明 AI-induced label noise、SCLNScore 或三种实验条件的真实研究目的。

## 研究者监控

使用界面中的“研究者”页查看聚合进度和输出产物。人工收集完成后运行：

```bash
python -m experiments.export_features --config configs/default.yaml --output outputs/features.csv --refresh-db
python -m experiments.train_sclnscore --features outputs/features.csv --output-dir outputs/scln
python -m experiments.evaluate_review --features outputs/scln/features_scored.csv --output-dir outputs/review
python -m experiments.generate_report --features outputs/scln/features_scored.csv --review-metrics outputs/review/review_policy_metrics.csv --output-dir outputs/report
```
