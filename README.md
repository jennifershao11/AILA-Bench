# AILA-Bench SCLN-Det MVP

这是一个用于 SCLN-Det 实验的端到端 MVP，覆盖 BDD100K 2D 检测标注导入、YOLO11 预标注、人工标注 Web 系统、行为轨迹记录、gold 自动判定、SCLNScore 训练与复审策略评估。

## 已包含模块

- FastAPI 后端：任务分配、图片读取、标注提交、事件记录、统计与产物下载。
- React 标注界面：三种实验条件由后端随机/顺序分配，标注员界面不暴露真实条件。
- 实验脚本：BDD100K 官方数据准备、YOLO11 推理、AI suggestion 导入、特征导出、SCLNScore 训练、复审策略评估和报告生成。
- 测试：bbox/匹配/错误类型、任务分配约束、API 行为、SCLNScore 训练评估。

## 当前正式数据状态

默认配置使用：

```bash
data/bdd100k_prepared/bdd100k_images_100k/100k/train
data/bdd100k_prepared/bdd100k_labels/100k/train
outputs/bdd100k/yolo11_predictions.jsonl
```

默认 pilot 规模为 300 张图，每张图创建 3 个任务，对应 `human_only`、`ai_assisted`、`ai_assisted_confidence`。

## 环境安装

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cd frontend
npm install
```

## 准备 BDD100K Pilot

如果官方 zip 已经放在 `data/bdd100k_official/`，运行：

```bash
python -m experiments.prepare_bdd100k --source-dir data/bdd100k_official --output-dir data/bdd100k_prepared --extract
python -m experiments.import_bdd100k \
  --config configs/default.yaml \
  --bdd-labels data/bdd100k_prepared/bdd100k_labels/100k/train \
  --image-root data/bdd100k_prepared/bdd100k_images_100k/100k/train \
  --limit 300 \
  --reset-db
python -m experiments.create_tasks --config configs/default.yaml
python -m experiments.yolo11_pipeline \
  --config configs/default.yaml \
  --dataset bdd100k \
  --split pilot \
  --limit 300 \
  --weights models/yolo11n.pt \
  --output outputs/bdd100k/yolo11_predictions.jsonl
python -m experiments.import_suggestions --config configs/default.yaml --input outputs/bdd100k/yolo11_predictions.jsonl
```

也可以使用正式流水线脚本：

```bash
python -m experiments.run_pipeline --dataset bdd100k --limit 300
```

## 启动人工标注系统

后端：

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8001
```

前端：

```bash
cd frontend
npm run dev -- --host 0.0.0.0 --port 5174
```

访问：

```text
http://<server-ip>:5174
```

标注员只需要停留在“标注”页，输入分配的参与者编号，点击“开始下一张”。

## 人工标注后生成实验结果

收集到人工提交后运行：

```bash
python -m experiments.export_features --config configs/default.yaml --output outputs/features.csv --refresh-db
python -m experiments.train_sclnscore --features outputs/features.csv --output-dir outputs/scln
python -m experiments.evaluate_review --features outputs/scln/features_scored.csv --output-dir outputs/review
python -m experiments.generate_report --features outputs/scln/features_scored.csv --review-metrics outputs/review/review_policy_metrics.csv --output-dir outputs/report
```

或：

```bash
python -m experiments.run_pipeline --dataset bdd100k --skip-import --skip-yolo --post-annotation
```

## 测试

```bash
python -m pytest
cd frontend
npm run build
```

## 目标类别

`car`、`pedestrian`、`rider`、`bus`、`truck`、`motorcycle`、`traffic light`、`traffic sign`

前端对标注员展示中文类别名，提交到后端和实验 CSV 的类别字段仍保留上述英文标准值。
