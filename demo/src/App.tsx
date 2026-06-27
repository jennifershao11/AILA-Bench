import { useState } from 'react';
import {
  ArrowRight,
  BarChart3,
  Eye,
  Target,
  Timer,
  Zap,
} from 'lucide-react';
import { cases, decisionLabel, humanReviewAvailable, type AIErrorType, type AnnotationCase } from './data/cases';
import { demoScene, classColor, boxStyleTokens } from './data/demoScene';
import { findings } from './data/findings';
import {
  rq1Data,
  rq2Data,
  rq3Data,
  rq4Data,
  rq5Data,
  benchmarkStats,
  studyStats,
} from './data/results';

type Condition = 'human_only' | 'ai_assisted' | 'ai_assisted_conf';
type ActiveRQ = 'rq1' | 'rq2' | 'rq3' | 'rq4' | 'rq5';

const COND = {
  human_only: '#0f6c78',
  ai_assisted: '#2f6fb0',
  ai_assisted_conf: '#7e57a3',
};
const POS = '#0f6c78';
const NEG = '#b23a48';

// RQ1–RQ3 & RQ5: benchmark exports. RQ4: appendix feature ablation (logistic regression).
const PH = 'xxx';
const SKELETON = '#c9c4ba';

function showLive(placeholder: boolean) {
  return !placeholder;
}

// Renders **bold** spans inside plain strings so we can highlight key phrases.
function RichText({ text }: { text: string }) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return (
    <>
      {parts.map((part, i) =>
        part.startsWith('**') && part.endsWith('**') ? (
          <strong key={i} className="font-semibold text-ink">
            {part.slice(2, -2)}
          </strong>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </>
  );
}

function SectionHeader({
  eyebrow,
  title,
  children,
}: {
  eyebrow: string;
  title: string;
  children?: React.ReactNode;
}) {
  return (
    <div className="text-center max-w-2xl mx-auto mb-14">
      <p className="eyebrow mb-3">{eyebrow}</p>
      <h2 className="display text-3xl md:text-[2.6rem] leading-[1.1] mb-4">{title}</h2>
      {children && <p className="text-muted text-lg leading-relaxed">{children}</p>}
    </div>
  );
}

function PlaceholderBanner() {
  return null;
}

function Navigation() {
  const [isOpen, setIsOpen] = useState(false);
  const navItems = [
    { label: 'Overview', href: '#overview' },
    { label: 'Demo', href: '#demo' },
    { label: 'Cases', href: '#cases' },
    { label: 'Results', href: '#results' },
  ];

  return (
    <nav className="sticky top-0 z-40 bg-paper/70 backdrop-blur-xl border-b border-line">
      <div className="max-w-6xl mx-auto px-5 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <a href="#" className="flex items-center gap-2.5 group">
            <span className="w-2.5 h-2.5 rounded-full bg-accent group-hover:scale-110 transition-transform" />
            <span className="text-[17px] font-semibold tracking-tight text-ink">AILA-Bench</span>
          </a>
          <div className="hidden md:flex items-center gap-1">
            {navItems.map((item) => (
              <a
                key={item.href}
                href={item.href}
                className="px-3.5 py-2 text-sm text-muted hover:text-ink transition-colors"
              >
                {item.label}
              </a>
            ))}
          </div>
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden inline-flex items-center gap-1.5 text-sm text-muted hover:text-ink"
          >
            Menu
            <span className={`transition-transform ${isOpen ? 'rotate-180' : ''}`}>▾</span>
          </button>
        </div>
        {isOpen && (
          <div className="md:hidden py-3 border-t border-line">
            {navItems.map((item) => (
              <a
                key={item.href}
                href={item.href}
                onClick={() => setIsOpen(false)}
                className="block px-2 py-2 text-sm text-muted hover:text-ink transition-colors"
              >
                {item.label}
              </a>
            ))}
          </div>
        )}
      </div>
    </nav>
  );
}

function Hero() {
  const stats = [
    { value: benchmarkStats.annotators.toLocaleString('en-US'), label: 'Annotators' },
    { value: benchmarkStats.images.toLocaleString('en-US'), label: 'BDD100K images' },
    { value: String(benchmarkStats.conditions), label: 'Conditions' },
    { value: String(benchmarkStats.numClasses), label: 'Object classes' },
  ];
  return (
    <section className="relative overflow-hidden">
      <div className="max-w-4xl mx-auto px-5 pt-20 pb-16 md:pt-28 md:pb-20 text-center">
        <p className="eyebrow mb-5">The AI-in-the-Loop Annotation Benchmark</p>
        <h1 className="display text-5xl md:text-7xl leading-[1.02] mb-6">AILA-Bench</h1>
        <p className="font-serif text-xl md:text-2xl text-ink/85 leading-snug max-w-3xl mx-auto mb-6">
          Can Model-in-the-Loop Annotation Be Safely Scaled? Auditing Suggestion-Conditioned
          Label Noise in Human–AI Data Pipelines
        </p>
        <div className="flex items-center justify-center gap-3 mb-8 text-sm">
          <span className="text-muted">Anonymous Authors</span>
          <span className="w-1 h-1 rounded-full bg-muted/50" />
          <span className="inline-flex items-center rounded-full border border-line bg-white/60 px-3 py-1 text-muted">
            Submission under review
          </span>
        </div>
        <p className="text-muted text-lg leading-relaxed max-w-2xl mx-auto mb-10">
          A benchmark for studying how annotators interact with AI suggestions in 2D object
          detection — <strong className="font-semibold text-ink">when they accept the wrong
          ones</strong>, and how to audit the resulting{' '}
          <strong className="font-semibold text-ink">Suggestion-Conditioned Label Noise (SCLN)</strong>.
        </p>
        <div className="flex flex-wrap items-center justify-center gap-3">
          <a
            href="#demo"
            className="inline-flex items-center gap-2 rounded-full btn-accent text-white px-6 py-3 text-sm font-medium shadow-card hover:-translate-y-0.5 hover:shadow-lift transition-all"
          >
            <Eye className="w-4 h-4" /> Explore the demo
          </a>
          <a
            href="#cases"
            className="inline-flex items-center gap-2 rounded-full border border-line bg-white/70 text-ink px-6 py-3 text-sm font-medium hover:bg-white transition-all"
          >
            Browse cases <ArrowRight className="w-4 h-4" />
          </a>
          <a
            href="#results"
            className="inline-flex items-center gap-2 rounded-full border border-line bg-white/70 text-ink px-6 py-3 text-sm font-medium hover:bg-white transition-all"
          >
            See results
          </a>
        </div>

        <div className="mt-16 flex flex-wrap items-stretch justify-center divide-x divide-line">
          {stats.map((s) => (
            <div key={s.label} className="px-7 py-2 min-w-[8rem]">
              <p className="font-serif text-3xl text-ink leading-none mb-1.5">{s.value}</p>
              <p className="text-xs uppercase tracking-wide text-muted">{s.label}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function OverviewSection() {
  const insightIcons: Record<string, React.ReactNode> = {
    'speed-accuracy': <Timer className="w-5 h-5" />,
    inheritance: <Zap className="w-5 h-5" />,
    'scln-random': <Target className="w-5 h-5" />,
    auprc: <BarChart3 className="w-5 h-5" />,
  };
  const keyInsights = findings.map((f) => ({
    icon: insightIcons[f.id] ?? <Target className="w-5 h-5" />,
    title: f.title,
    value: f.placeholder ? PH : f.value,
    desc: f.description,
  }));

  return (
    <section id="overview" className="py-24 scroll-mt-20">
      <div className="max-w-6xl mx-auto px-5">
        <SectionHeader eyebrow="Overview" title="What AILA-Bench measures">
          Headline findings from a controlled study of model-in-the-loop annotation, where the
          same images are labelled{' '}
          <strong className="font-semibold text-ink">with and without AI assistance</strong>.
        </SectionHeader>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
          {keyInsights.map((insight) => (
            <div key={insight.title} className="card p-6">
              <div className="inline-flex p-2.5 rounded-full bg-accent-tint text-accent mb-4">
                {insight.icon}
              </div>
              <p className="font-serif text-3xl text-ink leading-none mb-2">{insight.value}</p>
              <h4 className="text-sm font-semibold text-ink mb-1.5">{insight.title}</h4>
              <p className="text-sm text-muted leading-relaxed">
                <RichText text={insight.desc} />
              </p>
            </div>
          ))}
        </div>

        <div className="grid md:grid-cols-2 gap-5">
          <div className="card p-7">
            <h3 className="font-serif text-xl text-ink mb-5">Pilot scale (Table tab:rq1a)</h3>
            <ul className="space-y-3 text-sm mb-6">
              <li className="flex justify-between gap-4 border-b border-line pb-3">
                <span className="text-muted">Tasks per condition</span>
                <span className="text-ink font-mono">
                  {studyStats.tasksPerCondition.toLocaleString('en-US')}
                </span>
              </li>
              <li className="flex justify-between gap-4 border-b border-line pb-3">
                <span className="text-muted">Human-only labels</span>
                <span className="text-ink font-mono">
                  {studyStats.labelsByCondition.human_only.toLocaleString('en-US')}
                </span>
              </li>
              <li className="flex justify-between gap-4 border-b border-line pb-3">
                <span className="text-muted">AI-assisted labels</span>
                <span className="text-ink font-mono">
                  {studyStats.labelsByCondition.ai_assisted.toLocaleString('en-US')}
                </span>
              </li>
            </ul>
            <p className="text-xs text-muted leading-relaxed">{rq1Data.pilotNote}</p>
            <h4 className="text-xs uppercase tracking-wide text-muted mb-3">Conditions</h4>
            <ul className="space-y-3">
              {[
                { c: COND.human_only, t: 'Human Only', d: 'No AI assistance.' },
                { c: COND.ai_assisted, t: 'AI-Assisted', d: 'Suggestions without confidence.' },
                { c: COND.ai_assisted_conf, t: 'AI + Confidence', d: 'Suggestions with confidence scores.' },
              ].map((row) => (
                <li key={row.t} className="flex items-start gap-3">
                  <span
                    className="w-2.5 h-2.5 rounded-full mt-1.5 shrink-0"
                    style={{ backgroundColor: row.c }}
                  />
                  <div>
                    <span className="text-ink font-medium text-sm">{row.t}</span>
                    <p className="text-xs text-muted">{row.d}</p>
                  </div>
                </li>
              ))}
            </ul>
          </div>
          <div className="card p-7">
            <h3 className="font-serif text-xl text-ink mb-5">Recorded interaction traces</h3>
            <p className="text-sm text-muted mb-4">
              Every annotation event is logged, enabling counterfactual analysis of how AI
              suggestions shaped the final label.
            </p>
            <div className="flex flex-wrap gap-2">
              {benchmarkStats.traceFields.map((field) => (
                <span
                  key={field}
                  className="px-3 py-1.5 rounded-full bg-white/70 border border-line text-[13px] text-ink/80 font-mono"
                >
                  {field}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function DemoViewer() {
  const [condition, setCondition] = useState<Condition>('human_only');
  const { width: W, height: H, boxes } = demoScene;
  const conditions = [
    { id: 'human_only' as const, label: 'Human Only' },
    { id: 'ai_assisted' as const, label: 'AI-Assisted' },
    { id: 'ai_assisted_conf' as const, label: 'AI + Confidence' },
  ];

  return (
    <section id="demo" className="py-24 scroll-mt-20">
      <div className="max-w-6xl mx-auto px-5">
        <SectionHeader eyebrow="Interactive demo" title="One frame, three conditions">
          The same BDD100K frame under each annotation condition. Boxes and confidences are
          real <strong className="font-semibold text-ink">YOLOv8 nano</strong> predictions for
          this image.
        </SectionHeader>

        <div className="card p-6 md:p-8">
          <div className="flex justify-center mb-6">
            <div className="inline-flex items-center gap-1 rounded-full border border-line bg-white/70 p-1">
              {conditions.map((cond) => {
                const active = condition === cond.id;
                return (
                  <button
                    key={cond.id}
                    onClick={() => setCondition(cond.id)}
                    className="px-4 py-2 rounded-full text-sm font-medium transition-all"
                    style={
                      active
                        ? { backgroundColor: COND[cond.id], color: '#fff' }
                        : { color: '#5f6774' }
                    }
                  >
                    {cond.label}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="relative aspect-video rounded-xl overflow-hidden ring-1 ring-line shadow-card mb-6">
            <img
              src={demoScene.imagePath}
              alt="BDD100K street scene"
              className="absolute inset-0 w-full h-full object-cover"
            />
            {condition === 'human_only' && (
              <div className="absolute top-3 left-3 px-3 py-1.5 rounded-full bg-white/90 text-ink text-xs font-medium shadow-card">
                Empty canvas — annotator draws every box from scratch
              </div>
            )}
            {condition !== 'human_only' &&
              boxes.map((box) => {
                const [x, y, w, h] = box.bbox;
                const color = classColor(box.category);
                return (
                  <div
                    key={box.id}
                    className="absolute border-2 rounded-sm"
                    style={{
                      left: `${(x / W) * 100}%`,
                      top: `${(y / H) * 100}%`,
                      width: `${(w / W) * 100}%`,
                      height: `${(h / H) * 100}%`,
                      borderColor: color,
                    }}
                  >
                    <div
                      className="absolute -top-5 left-0 px-1.5 py-0.5 rounded text-[11px] font-medium text-white whitespace-nowrap"
                      style={{ backgroundColor: color }}
                    >
                      {box.category}
                      {condition === 'ai_assisted_conf' && (
                        <span className="ml-1 opacity-80">{Math.round(box.confidence * 100)}%</span>
                      )}
                    </div>
                  </div>
                );
              })}
          </div>

          <div className="grid md:grid-cols-3 gap-4">
            {[
              {
                id: 'human_only' as const,
                t: 'Human Only',
                d: 'No AI suggestions shown. The annotator draws everything.',
              },
              {
                id: 'ai_assisted' as const,
                t: 'AI-Assisted',
                d: 'AI provides suggestions. The annotator can accept, edit, or reject.',
              },
              {
                id: 'ai_assisted_conf' as const,
                t: 'AI + Confidence',
                d: 'Suggestions include confidence scores, shown as a percentage.',
              },
            ].map((card) => {
              const active = condition === card.id;
              return (
                <div
                  key={card.id}
                  className="rounded-xl p-5 border transition-all"
                  style={{
                    borderColor: active ? COND[card.id] : 'rgba(22,33,50,0.12)',
                    backgroundColor: active ? `${COND[card.id]}14` : 'rgba(255,255,255,0.6)',
                  }}
                >
                  <h4 className="font-medium text-ink mb-1">{card.t}</h4>
                  <p className="text-sm text-muted leading-relaxed">{card.d}</p>
                </div>
              );
            })}
          </div>

          <p className="text-center text-xs text-muted mt-6">
            Frame {demoScene.externalId} · {demoScene.source} · {demoScene.model} suggestions
          </p>
        </div>
      </div>
    </section>
  );
}

const GT_COLOR = boxStyleTokens.gtColor;
const AI_FOCUS_COLOR = boxStyleTokens.aiFocusColor;
const FINAL_COLOR = boxStyleTokens.finalColor;

function CaseFrame({
  imagePath,
  width,
  height,
  boxes,
  className,
}: {
  imagePath: string;
  width: number;
  height: number;
  boxes: {
    bbox: [number, number, number, number];
    color: string;
    label?: string;
    zIndex?: number;
    labelPosition?: 'top' | 'bottom';
    labelAlign?: 'left' | 'right';
  }[];
  className?: string;
}) {
  return (
    <div className={`relative overflow-visible rounded-lg bg-ink/5 ring-1 ring-line ${className ?? ''}`}>
      <img
        src={imagePath}
        alt=""
        className="absolute inset-0 w-full h-full object-cover rounded-lg"
      />
      {boxes.map((b, i) => {
        const [x, y, w, h] = b.bbox;
        const labelAbove = b.labelPosition !== 'bottom';
        const alignRight = b.labelAlign === 'right';
        return (
          <div
            key={i}
            className="absolute border-2 rounded-sm overflow-visible"
            style={{
              left: `${(x / width) * 100}%`,
              top: `${(y / height) * 100}%`,
              width: `${(w / width) * 100}%`,
              height: `${(h / height) * 100}%`,
              borderColor: b.color,
              zIndex: b.zIndex ?? 10,
            }}
          >
            {b.label && (
              <span
                className={`absolute px-1 py-0.5 text-[10px] font-medium text-white whitespace-nowrap ${
                  labelAbove
                    ? `${alignRight ? 'right-0' : 'left-0'} bottom-full rounded-tl rounded-tr`
                    : `${alignRight ? 'right-0' : 'left-0'} top-full rounded-bl rounded-br`
                }`}
                style={{ backgroundColor: b.color }}
              >
                {b.label}
              </span>
            )}
          </div>
        );
      })}
    </div>
  );
}

// GT + AI + optional human final for case gallery detail view.
function caseGalleryBoxes(c: AnnotationCase, withLabels = true) {
  const out: {
    bbox: [number, number, number, number];
    color: string;
    label?: string;
    zIndex: number;
    labelPosition: 'top' | 'bottom';
    labelAlign?: 'left' | 'right';
  }[] = [];

  if (c.focus.ai) {
    const conf = c.focus.ai.confidence;
    const pct = conf != null ? ` ${Math.round(conf * 100)}%` : '';
    out.push({
      bbox: c.focus.ai.bbox,
      color: AI_FOCUS_COLOR,
      label: withLabels ? `AI: ${c.focus.ai.class}${pct}` : 'AI',
      zIndex: 10,
      labelPosition: c.id === 'case-3' ? 'top' : 'bottom',
    });
  }
  if (c.focus.gt) {
    out.push({
      bbox: c.focus.gt.bbox,
      color: GT_COLOR,
      label: withLabels ? `GT: ${c.focus.gt.class}` : 'GT',
      zIndex: 20,
      labelPosition: 'top',
    });
  }
  if (c.humanReview) {
    const fin = c.humanReview.final;
    const err =
      fin.errorType !== 'correct' ? ` (${fin.errorType.replace(/_/g, ' ')})` : '';
    out.push({
      bbox: fin.bbox,
      color: FINAL_COLOR,
      label: withLabels ? `Final: ${fin.class}${err}` : 'Final',
      zIndex: 30,
      labelPosition: 'top',
      labelAlign: 'right',
    });
  }
  return out;
}

function CaseGallery() {
  const [selectedCase, setSelectedCase] = useState<string>(cases[0].id);
  const errorLabels: Record<AIErrorType, string> = {
    class: 'Class confusion',
    localization: 'Localization',
    hallucination: 'Hallucination',
    missing: 'Missing object',
    duplicate: 'Duplicate',
    wrong_object: 'Wrong object',
    correct: 'Correct',
  };
  const errorColors: Record<AIErrorType, string> = {
    class: 'bg-rose-50 text-rose-700 border-rose-200',
    localization: 'bg-amber-50 text-amber-700 border-amber-200',
    hallucination: 'bg-violet-50 text-violet-700 border-violet-200',
    missing: 'bg-cyan-50 text-cyan-700 border-cyan-200',
    duplicate: 'bg-pink-50 text-pink-700 border-pink-200',
    wrong_object: 'bg-orange-50 text-orange-700 border-orange-200',
    correct: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  };

  const c = cases.find((x) => x.id === selectedCase) ?? cases[0];
  const gt = c.focus.gt;
  const ai = c.focus.ai;
  const hr = c.humanReview;

  return (
    <section id="cases" className="py-24 scroll-mt-20 bg-white/45 border-y border-line">
      <div className="max-w-7xl mx-auto px-5">
        <SectionHeader eyebrow="Case gallery" title="Anatomy of suggestion-conditioned errors">
          Real BDD100K frames with{' '}
          <strong className="font-semibold text-ink">ground truth, YOLOv8 nano suggestions, and human
          final labels</strong> from our annotation study submissions. Each case highlights{' '}
          <strong className="font-semibold text-ink">one focal object</strong> for clarity—not the
          full set of boxes on the image.
        </SectionHeader>

        <div className="grid lg:grid-cols-3 gap-6 items-start">
          {/* Detail panel */}
          <div className="lg:col-span-2 lg:order-2 card p-6 md:p-7">
            <div className="flex items-start justify-between gap-3 mb-2">
              <h3 className="font-serif text-2xl text-ink">{c.title}</h3>
              <span
                className={`shrink-0 px-2.5 py-1 rounded-full text-xs border ${errorColors[c.errorType]}`}
              >
                {errorLabels[c.errorType]}
              </span>
            </div>
            <p className="text-muted mb-5 leading-relaxed">{c.description}</p>

            <CaseFrame
              imagePath={c.imagePath}
              width={c.width}
              height={c.height}
              boxes={caseGalleryBoxes(c)}
              className="aspect-video"
            />
            {c.errorType === 'hallucination' && hr?.decision === 'accept' && (
              <p className="text-xs text-amber-800/90 mt-2 leading-relaxed bg-amber-50/80 border border-amber-200/80 rounded-lg px-3 py-2">
                <strong className="font-semibold">Note:</strong> Ground truth has no bus here, but
                the annotator <strong className="font-semibold">accepted</strong> the AI bus box
                (wrong_object) rather than deleting it.
              </p>
            )}
            {!gt && ai && c.errorType !== 'hallucination' && (
              <p className="text-xs text-muted mt-2 leading-relaxed">
                <strong className="font-semibold text-ink">No ground-truth box</strong> for this
                object — the model proposed a detection where none exists (hallucination).
              </p>
            )}
            {gt && !ai && (
              <p className="text-xs text-muted mt-2 leading-relaxed">
                <strong className="font-semibold text-ink">No AI box</strong> — this ground-truth
                object was missed by the detector (missing detection).
              </p>
            )}
            <div className="flex flex-wrap items-center gap-4 mt-3 text-xs">
              {gt && (
                <span className="flex items-center gap-1.5">
                  <span className="w-3 h-3 rounded-sm" style={{ backgroundColor: GT_COLOR }} />
                  <span className="text-muted">Ground truth</span>
                </span>
              )}
              {ai && (
                <span className="flex items-center gap-1.5">
                  <span
                    className="w-3 h-3 rounded-sm"
                    style={{ backgroundColor: COND.ai_assisted }}
                  />
                  <span className="text-muted">AI suggestion</span>
                </span>
              )}
              {hr && (
                <span className="flex items-center gap-1.5">
                  <span className="w-3 h-3 rounded-sm" style={{ backgroundColor: FINAL_COLOR }} />
                  <span className="text-muted">Human final</span>
                </span>
              )}
            </div>
            <p className="text-[11px] text-muted/90 mb-5 leading-relaxed">
              Display note: boxes shown are the focal pair for this error type only. Annotators worked
              on the full frame with all objects; other GT, AI, and final boxes are omitted here for
              readability.
            </p>

            <div className="grid sm:grid-cols-2 gap-4">
              <div className="rounded-xl bg-white/70 border border-line p-4">
                <p className="text-xs uppercase tracking-wide text-muted mb-3">
                  Model vs. ground truth <span className="text-teal">· real</span>
                </p>
                <div className="grid grid-cols-2 gap-y-2 gap-x-4 text-sm">
                  <div>
                    <span className="text-muted">AI class</span>{' '}
                    <span className="text-ink">{ai ? ai.class : 'none'}</span>
                  </div>
                  <div>
                    <span className="text-muted">AI conf.</span>{' '}
                    <span className="text-ink font-mono">
                      {ai?.confidence != null ? `${Math.round(ai.confidence * 100)}%` : '—'}
                    </span>
                  </div>
                  <div>
                    <span className="text-muted">GT class</span>{' '}
                    <span className="text-ink">{gt ? gt.class : 'none'}</span>
                  </div>
                  <div>
                    <span className="text-muted">GT–AI IoU</span>{' '}
                    <span className="text-ink font-mono">
                      {gt && ai ? c.focus.iou.toFixed(2) : '—'}
                    </span>
                  </div>
                </div>
                <p className="mt-2.5 text-[11px] text-muted/80">
                  Frame {c.externalId} · BDD100K · YOLOv8 nano
                </p>
              </div>

              <div className="rounded-xl bg-white/70 border border-line p-4">
                <p className="text-xs uppercase tracking-wide text-muted mb-3">
                  Human review{' '}
                  {hr ? (
                    <span className="text-teal">· study trace</span>
                  ) : (
                    <span className="text-muted/60">· pending</span>
                  )}
                </p>
                {hr ? (
                  <>
                    <div className="grid grid-cols-2 gap-y-2 gap-x-4 text-sm">
                      <div>
                        <span className="text-muted">Decision</span>{' '}
                        <span className="text-ink">{decisionLabel(hr.decision)}</span>
                      </div>
                      <div>
                        <span className="text-muted">Final class</span>{' '}
                        <span className="text-ink">{hr.final.class}</span>
                      </div>
                      <div>
                        <span className="text-muted">Final error</span>{' '}
                        <span className="text-ink font-mono text-xs">{hr.final.errorType}</span>
                      </div>
                      <div>
                        <span className="text-muted">AI→final IoU</span>{' '}
                        <span className="text-ink font-mono">
                          {hr.aiFinalIou != null ? hr.aiFinalIou.toFixed(2) : '—'}
                        </span>
                      </div>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="grid grid-cols-2 gap-y-2 gap-x-4 text-sm">
                      <div>
                        <span className="text-muted">Decision</span> <span className="text-ink">{PH}</span>
                      </div>
                      <div>
                        <span className="text-muted">Final box</span> <span className="text-ink">{PH}</span>
                      </div>
                    </div>
                    <p className="mt-3 text-[11px] leading-relaxed text-muted/90">
                      Human trace not loaded for this case.
                    </p>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Case list */}
          <div className="space-y-3 lg:order-1">
            {cases.map((item) => {
              const selected = item.id === selectedCase;
              const conf = item.focus.ai?.confidence;
              return (
                <button
                  key={item.id}
                  onClick={() => setSelectedCase(item.id)}
                  className={`w-full text-left card p-3 flex gap-3 items-center transition-all hover:-translate-y-0.5 hover:shadow-lift ${
                    selected ? 'ring-2 ring-accent' : ''
                  }`}
                >
                  <CaseFrame
                    imagePath={item.imagePath}
                    width={item.width}
                    height={item.height}
                    boxes={caseGalleryBoxes(item, false)}
                    className="w-28 shrink-0 aspect-video"
                  />
                  <div className="min-w-0 flex-1">
                    <h4 className="font-medium text-ink text-sm leading-snug mb-1.5 truncate">
                      {item.title}
                    </h4>
                    <span
                      className={`inline-block px-2 py-0.5 rounded-full text-[11px] border ${errorColors[item.errorType]}`}
                    >
                      {errorLabels[item.errorType]}
                    </span>
                    <p className="text-[11px] text-muted/70 mt-1.5 font-mono">
                      {conf != null ? `AI ${Math.round(conf * 100)}%` : 'no AI box'}
                      {item.humanReview
                        ? ` · ${decisionLabel(item.humanReview.decision)}`
                        : ' · pending'}
                    </p>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        <p className="text-center text-xs text-muted mt-8 max-w-2xl mx-auto">
          Images, GT, and detector boxes are <strong className="font-semibold text-ink">real BDD100K
          data</strong> (YOLOv8 nano predictions).
          {humanReviewAvailable ? (
            <>
              {' '}
              Human final labels and decisions are from our{' '}
              <strong className="font-semibold text-ink">annotation study submissions</strong> (exported
              task traces).
            </>
          ) : (
            <>
              {' '}
              Human traces are shown where exported in{' '}
              <code className="text-ink/80">cases_human_review.json</code>.
            </>
          )}
        </p>
      </div>
    </section>
  );
}

function ResultsExplorer() {
  const [activeRQ, setActiveRQ] = useState<ActiveRQ>('rq1');
  const rqTabs: { id: ActiveRQ; title: string; question: string }[] = [
    { id: 'rq1', title: 'RQ1', question: 'Error modes' },
    { id: 'rq2', title: 'RQ2', question: 'Confidence' },
    { id: 'rq3', title: 'RQ3', question: 'Detection' },
    { id: 'rq4', title: 'RQ4', question: 'Ablation' },
    { id: 'rq5', title: 'RQ5', question: 'Transfer' },
  ];

  return (
    <section id="results" className="py-24 scroll-mt-20">
      <div className="max-w-6xl mx-auto px-5">
        <SectionHeader eyebrow="Results" title="Five research questions">
          RQ1–RQ3 report the {studyStats.pilot} ({studyStats.tasksPerCondition.toLocaleString('en-US')}{' '}
          tasks per condition). RQ4 is the{' '}
          <strong className="font-semibold text-ink">appendix feature ablation</strong> (
          {rq4Data.labels.toLocaleString('en-US')} labels; {rq4Data.testLabels.toLocaleString('en-US')}{' '}
          held-out test). RQ5 is cross-dataset transfer on{' '}
          {rq5Data.nuImagesImages.toLocaleString('en-US')} nuImages images.
        </SectionHeader>

        <div className="flex flex-wrap gap-2 mb-8 justify-center">
          {rqTabs.map((tab) => {
            const active = activeRQ === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveRQ(tab.id)}
                className={`px-4 py-2.5 rounded-full text-sm transition-all border ${
                  active
                    ? 'bg-ink text-paper border-ink'
                    : 'bg-white/70 text-muted border-line hover:text-ink'
                }`}
              >
                <span className="font-semibold">{tab.title}</span>
                <span className="mx-1.5 opacity-40">·</span>
                <span className="opacity-80">{tab.question}</span>
              </button>
            );
          })}
        </div>

        <div className="card p-6 md:p-8">
          {activeRQ === 'rq1' && <RQ1Panel />}
          {activeRQ === 'rq2' && <RQ2Panel />}
          {activeRQ === 'rq3' && <RQ3Panel />}
          {activeRQ === 'rq4' && <RQ4Panel />}
          {activeRQ === 'rq5' && <RQ5Panel />}
        </div>
      </div>
    </section>
  );
}

function Answer({ text, color }: { text: string; color: string }) {
  return (
    <div
      className="mt-7 p-4 rounded-xl bg-white/70 sheen-metal border border-line border-l-4"
      style={{ borderLeftColor: color }}
    >
      <p className="text-muted leading-relaxed">
        <RichText text={text} />
      </p>
    </div>
  );
}

function PanelHeading({ title, question }: { title: string; question: string }) {
  return (
    <div className="mb-7">
      <h3 className="font-serif text-2xl text-ink mb-1.5">{title}</h3>
      <p className="text-muted">{question}</p>
    </div>
  );
}

function BarChart({
  data,
  labels,
  maxValue,
  suffix = '',
  live = true,
}: {
  data: { label: string; values: number[]; color: string }[];
  labels: string[];
  maxValue: number;
  suffix?: string;
  live?: boolean;
}) {
  return (
    <div className="space-y-4">
      {labels.map((label, i) => (
        <div key={label}>
          <span className="text-sm text-muted">{label}</span>
          <div className="flex gap-1.5 mt-1.5">
            {data.map((series) => (
              <div
                key={series.label}
                className="h-6 rounded-full flex items-center justify-end pr-2.5 text-xs font-medium"
                style={
                  live
                    ? {
                        width: `${Math.max((series.values[i] / maxValue) * 100, series.values[i] > 0 ? 9 : 0)}%`,
                        backgroundColor: series.color,
                        color: '#fff',
                      }
                    : { width: '40%', backgroundColor: SKELETON, color: '#46505f' }
                }
              >
                {live ? `${series.values[i]}${suffix}` : PH}
              </div>
            ))}
          </div>
        </div>
      ))}
      <div className="flex flex-wrap gap-4 pt-2">
        {data.map((series) => (
          <div key={series.label} className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full" style={{ backgroundColor: series.color }} />
            <span className="text-xs text-muted">{series.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function MeterRow({
  label,
  display,
  pct,
  color,
  live = true,
}: {
  label: string;
  display: string;
  pct: number;
  color: string;
  live?: boolean;
}) {
  return (
    <div>
      <div className="flex justify-between text-sm mb-1.5">
        <span className="text-muted">{label}</span>
        <span className="text-ink font-medium">{live ? display : PH}</span>
      </div>
      <div className="h-3.5 rounded-full bg-ink/[0.06] overflow-hidden">
        <div
          className="h-full rounded-full"
          style={{
            width: live ? `${pct}%` : '42%',
            backgroundColor: live ? color : SKELETON,
          }}
        />
      </div>
    </div>
  );
}

function RQ1Panel() {
  const live = showLive(rq1Data.placeholder);
  const conditionNames = ['Human-only', 'AI-assisted', 'AI + Confidence'];
  return (
    <div>
      <PanelHeading title={rq1Data.title} question={rq1Data.question} />
      <p className="text-sm text-muted mb-6 leading-relaxed">{rq1Data.pilotNote}</p>
      <h4 className="text-xs uppercase tracking-wide text-muted mb-3">
        Task scale, accuracy, and FDER (Table tab:rq1a)
      </h4>
      <div className="overflow-x-auto mb-8">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="border-b border-line text-left text-muted text-xs uppercase tracking-wide">
              <th className="py-2 pr-3 font-medium">Condition</th>
              <th className="py-2 pr-3 font-medium text-right">Tasks</th>
              <th className="py-2 pr-3 font-medium text-right">Labels</th>
              <th className="py-2 pr-3 font-medium text-right">Acc.</th>
              <th className="py-2 pr-3 font-medium text-right">FDER</th>
              <th className="py-2 pr-3 font-medium text-right">BBox</th>
              <th className="py-2 pr-3 font-medium text-right">Class</th>
              <th className="py-2 pr-3 font-medium text-right">FP</th>
              <th className="py-2 pr-3 font-medium text-right">Miss</th>
              <th className="py-2 font-medium text-right">Other</th>
            </tr>
          </thead>
          <tbody>
            {rq1Data.conditions.map((row, i) => (
              <tr key={row.key} className="border-b border-line/60">
                <td className="py-2.5 pr-3 text-ink font-medium">{conditionNames[i]}</td>
                <td className="py-2.5 pr-3 font-mono text-right">
                  {live ? row.tasks.toLocaleString('en-US') : PH}
                </td>
                <td className="py-2.5 pr-3 font-mono text-right">
                  {live ? row.labels.toLocaleString('en-US') : PH}
                </td>
                <td className="py-2.5 pr-3 font-mono text-right">
                  {live ? `${row.accuracy.toFixed(1)}%` : PH}
                </td>
                <td className="py-2.5 pr-3 font-mono text-right">
                  {live ? `${row.fder.toFixed(1)}%` : PH}
                </td>
                <td className="py-2.5 pr-3 font-mono text-right">
                  {live ? `${row.bbox.toFixed(1)}%` : PH}
                </td>
                <td className="py-2.5 pr-3 font-mono text-right">
                  {live ? `${row.class.toFixed(1)}%` : PH}
                </td>
                <td className="py-2.5 pr-3 font-mono text-right">
                  {live ? `${row.fp.toFixed(1)}%` : PH}
                </td>
                <td className="py-2.5 pr-3 font-mono text-right">
                  {live ? `${row.miss.toFixed(1)}%` : PH}
                </td>
                <td className="py-2.5 font-mono text-right">
                  {live ? `${row.other.toFixed(1)}%` : PH}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <h4 className="text-xs uppercase tracking-wide text-muted mb-4">
        Error composition by condition (% of labels)
      </h4>
      <BarChart
        live={live}
        data={[
          { label: 'Human-only', values: rq1Data.fderByCondition.humanOnly, color: COND.human_only },
          { label: 'AI-assisted', values: rq1Data.fderByCondition.aiAssisted, color: COND.ai_assisted },
          {
            label: 'AI + Confidence',
            values: rq1Data.fderByCondition.aiAssistedConf,
            color: COND.ai_assisted_conf,
          },
        ]}
        labels={rq1Data.fderByCondition.labels}
        maxValue={15}
        suffix="%"
      />
      <Answer color={POS} text={rq1Data.answer} />
    </div>
  );
}

function RQ2Panel() {
  const live = showLive(rq2Data.placeholder);
  return (
    <div>
      <PanelHeading title={rq2Data.title} question={rq2Data.question} />
      <p className="text-sm text-muted mb-6 leading-relaxed">
        {rq2Data.summary.aiLinkedLabels.toLocaleString('en-US')} source-linked final labels in the
        pilot (Table tab:rq2a). Same error inherited means the final label has the same error type
        as an erroneous AI suggestion.
      </p>
      <h4 className="text-xs uppercase tracking-wide text-muted mb-3">
        By AI confidence bucket (Table tab:rq2a)
      </h4>
      <div className="overflow-x-auto mb-8">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="border-b border-line text-left text-muted text-xs uppercase tracking-wide">
              <th className="py-2 pr-4 font-medium">AI conf.</th>
              <th className="py-2 pr-4 font-medium text-right">AI-linked labels</th>
              <th className="py-2 pr-4 font-medium text-right">AI wrong</th>
              <th className="py-2 pr-4 font-medium text-right">Same error inherited</th>
              <th className="py-2 font-medium text-right">Final error</th>
            </tr>
          </thead>
          <tbody>
            {rq2Data.byConfidence.map((row) => (
              <tr key={row.bucket} className="border-b border-line/60">
                <td className="py-2.5 pr-4 font-mono text-ink">{row.bucket}</td>
                <td className="py-2.5 pr-4 font-mono text-right">
                  {live ? row.aiLinkedLabels.toLocaleString('en-US') : PH}
                </td>
                <td className="py-2.5 pr-4 font-mono text-right">
                  {live ? `${row.aiWrongRate.toFixed(1)}%` : PH}
                </td>
                <td className="py-2.5 pr-4 font-mono text-right">
                  {live ? `${row.sameErrorInherited.toFixed(1)}%` : PH}
                </td>
                <td className="py-2.5 font-mono text-right">
                  {live ? `${row.finalErrorRate.toFixed(1)}%` : PH}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <h4 className="text-xs uppercase tracking-wide text-muted mb-4">
        Same-error inheritance vs. AI-wrong rate
      </h4>
      <BarChart
        live={live}
        data={[
          {
            label: 'Same error inherited',
            values: rq2Data.inheritanceByConfidence.sameErrorInherited,
            color: NEG,
          },
          {
            label: 'AI suggestion wrong (context)',
            values: rq2Data.inheritanceByConfidence.aiWrongRate,
            color: '#94a3b8',
          },
        ]}
        labels={rq2Data.inheritanceByConfidence.labels}
        maxValue={100}
        suffix="%"
      />
      <Answer color={COND.ai_assisted_conf} text={rq2Data.answer} />
    </div>
  );
}

function RQ3Panel() {
  const live = showLive(rq3Data.placeholder);
  return (
    <div>
      <PanelHeading title={rq3Data.title} question={rq3Data.question} />
      <p className="text-sm text-muted mb-5 leading-relaxed">{rq3Data.scorerNote}</p>
      <div className="flex flex-wrap gap-4 mb-6 p-4 rounded-xl bg-teal/5 border border-teal/15 text-sm">
        <span>
          <span className="text-muted">AUROC </span>
          <span className="font-mono text-ink">{live ? rq3Data.sclnMetrics.auroc.toFixed(3) : PH}</span>
        </span>
        <span>
          <span className="text-muted">AUPRC </span>
          <span className="font-mono text-ink">{live ? rq3Data.sclnMetrics.auprc.toFixed(3) : PH}</span>
        </span>
        <span>
          <span className="text-muted">Random baseline AUPRC </span>
          <span className="font-mono text-ink">
            {live ? rq3Data.sclnMetrics.randomAuprcBaseline.toFixed(3) : PH}
          </span>
        </span>
      </div>
      <div className="overflow-x-auto -mx-2">
        <table className="w-full text-sm min-w-[42rem]">
          <thead>
            <tr className="border-b border-line text-xs uppercase tracking-wide text-muted">
              <th className="text-left py-3 px-3 font-medium">Policy</th>
              <th className="text-right py-3 px-3 font-medium">AUPRC</th>
              <th className="text-right py-3 px-3 font-medium">P@1%</th>
              <th className="text-right py-3 px-3 font-medium">P@5%</th>
              <th className="text-right py-3 px-3 font-medium">R@5%</th>
              <th className="text-right py-3 px-3 font-medium">R@10%</th>
              <th className="text-right py-3 px-3 font-medium">R@20%</th>
            </tr>
          </thead>
          <tbody>
            {rq3Data.policies.map((policy) => {
              const highlight = policy.name === 'SCLNScore';
              return (
                <tr
                  key={policy.name}
                  className="border-b border-line last:border-0"
                  style={highlight ? { backgroundColor: 'rgba(15,108,120,0.07)' } : undefined}
                >
                  <td className="py-3 px-3">
                    <span className={highlight ? 'text-teal font-semibold' : 'text-ink/80'}>
                      {policy.name}
                    </span>
                  </td>
                  <td className="text-right py-3 px-3 text-ink font-mono">
                    {live
                      ? policy.auprc != null
                        ? policy.auprc.toFixed(3)
                        : '—'
                      : PH}
                  </td>
                  <td className="text-right py-3 px-3 text-ink font-mono">
                    {live ? `${(policy.precisionAt1 * 100).toFixed(1)}%` : PH}
                  </td>
                  <td className="text-right py-3 px-3 text-ink font-mono">
                    {live ? `${(policy.precisionAt5 * 100).toFixed(1)}%` : PH}
                  </td>
                  <td className="text-right py-3 px-3 text-ink font-mono">
                    {live ? `${(policy.recallAt5 * 100).toFixed(1)}%` : PH}
                  </td>
                  <td className="text-right py-3 px-3 text-ink font-mono">
                    {live ? `${(policy.recallAt10 * 100).toFixed(1)}%` : PH}
                  </td>
                  <td className="text-right py-3 px-3 text-ink font-mono">
                    {live ? `${(policy.recallAt20 * 100).toFixed(1)}%` : PH}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <p className="text-xs text-muted mt-3 leading-relaxed">
        <strong className="font-medium text-ink/80">AUPRC</strong> is computed for the trained
        SCLNScore ranker only; other policies are heuristic rankers without a global score curve
        (random baseline AUPRC ≈ {live ? rq3Data.sclnMetrics.randomAuprcBaseline.toFixed(3) : PH}{' '}
        shown above).
      </p>
      <Answer color={COND.human_only} text={rq3Data.answer} />
    </div>
  );
}

function RQ4Panel() {
  const live = showLive(rq4Data.placeholder);
  const drops = [...rq4Data.groups].sort((a, b) => b.auprcDrop - a.auprcDrop);
  const maxDrop = Math.max(...drops.map((g) => g.auprcDrop));

  return (
    <div>
      <PanelHeading title={rq4Data.title} question={rq4Data.question} />
      <p className="text-sm text-muted mb-6 leading-relaxed">{rq4Data.appendixNote}</p>
      <p className="text-sm text-muted mb-6 leading-relaxed">
        {rq4Data.modelLabel}. Features grouped into AI, Trace, Object, Scene, and Interface+Time (
        {rq4Data.featureCount} total), trained on {rq4Data.labels.toLocaleString('en-US')} final
        labels with image-level train/test split. Test set:{' '}
        {rq4Data.testLabels.toLocaleString('en-US')} labels, error rate {rq4Data.testErrorRate}%
        (random AUPRC baseline {rq4Data.randomAuprcBaseline.toFixed(3)}).
      </p>

      <div className="grid sm:grid-cols-3 gap-4 mb-8">
        <div className="rounded-xl bg-white/70 border border-line p-4">
          <p className="text-xs uppercase tracking-wide text-muted mb-1">Full model</p>
          <p className="text-ink font-mono text-lg">
            {live ? (
              <>
                AUPRC {rq4Data.fullModel.auprc.toFixed(3)}{' '}
                <span className="text-sm text-muted">· AUROC {rq4Data.fullModel.auroc.toFixed(3)}</span>
              </>
            ) : (
              PH
            )}
          </p>
        </div>
        <div className="rounded-xl bg-white/70 border border-line p-4">
          <p className="text-xs uppercase tracking-wide text-muted mb-1">Random baseline</p>
          <p className="text-ink font-mono text-lg">
            {live ? `AUPRC ${rq4Data.randomAuprcBaseline.toFixed(3)}` : PH}
          </p>
        </div>
        <div className="rounded-xl bg-white/70 border border-line p-4">
          <p className="text-xs uppercase tracking-wide text-muted mb-1">Strongest group alone</p>
          <p className="text-ink font-mono text-lg">
            {live ? `Object AUPRC ${rq4Data.groups[0].auprc.toFixed(3)}` : PH}
          </p>
        </div>
      </div>

      <h4 className="text-xs uppercase tracking-wide text-muted mb-3">
        Feature-group ablation (group-only models)
      </h4>
      <div className="overflow-x-auto mb-8">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="border-b border-line text-left text-muted text-xs uppercase tracking-wide">
              <th className="py-2 pr-4 font-medium">Group</th>
              <th className="py-2 pr-4 font-medium">#Feat.</th>
              <th className="py-2 pr-4 font-medium">AUROC</th>
              <th className="py-2 pr-4 font-medium">AUPRC</th>
              <th className="py-2 pr-4 font-medium">P@1%</th>
              <th className="py-2 pr-4 font-medium">R@10%</th>
              <th className="py-2 font-medium">ΔAUPRC</th>
            </tr>
          </thead>
          <tbody>
            {rq4Data.groups.map((g) => (
              <tr key={g.name} className="border-b border-line/60">
                <td className="py-2.5 pr-4 text-ink font-medium">{g.name}</td>
                <td className="py-2.5 pr-4 font-mono text-muted">{g.featureCount}</td>
                <td className="py-2.5 pr-4 font-mono">{live ? g.auroc.toFixed(3) : PH}</td>
                <td className="py-2.5 pr-4 font-mono">{live ? g.auprc.toFixed(3) : PH}</td>
                <td className="py-2.5 pr-4 font-mono">{live ? g.precisionAt1.toFixed(3) : PH}</td>
                <td className="py-2.5 pr-4 font-mono">{live ? g.recallAt10.toFixed(3) : PH}</td>
                <td className="py-2.5 font-mono" style={{ color: NEG }}>
                  {live ? g.auprcDrop.toFixed(3) : PH}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h4 className="text-xs uppercase tracking-wide text-muted mb-4">
        AUPRC drop when removing each group from the full model
      </h4>
      <div className="space-y-4 mb-8">
        {drops.map((g) => (
          <div key={g.name}>
            <div className="flex justify-between text-sm mb-1.5">
              <span className="text-muted">w/o {g.name}</span>
              <span className="text-ink font-medium font-mono">
                {live ? `−${g.auprcDrop.toFixed(3)} AUPRC` : PH}
              </span>
            </div>
            <div className="h-3.5 rounded-full bg-ink/[0.06] overflow-hidden">
              <div
                className="h-full rounded-full"
                style={{
                  width: live ? `${(g.auprcDrop / maxDrop) * 100}%` : '42%',
                  backgroundColor: live ? NEG : SKELETON,
                }}
              />
            </div>
          </div>
        ))}
      </div>

      <h4 className="text-xs uppercase tracking-wide text-muted mb-3">Top single-feature predictors</h4>
      <div className="overflow-x-auto mb-8">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="border-b border-line text-left text-muted text-xs uppercase tracking-wide">
              <th className="py-2 pr-4 font-medium">Feature</th>
              <th className="py-2 pr-4 font-medium">Group</th>
              <th className="py-2 pr-4 font-medium">AUROC</th>
              <th className="py-2 pr-4 font-medium">AUPRC</th>
              <th className="py-2 font-medium">Lift</th>
            </tr>
          </thead>
          <tbody>
            {rq4Data.topFeatures.map((f) => (
              <tr key={f.name} className="border-b border-line/60">
                <td className="py-2.5 pr-4 font-mono text-xs text-ink">{f.name}</td>
                <td className="py-2.5 pr-4 text-muted">{f.group}</td>
                <td className="py-2.5 pr-4 font-mono">{live ? f.auroc.toFixed(3) : PH}</td>
                <td className="py-2.5 pr-4 font-mono">{live ? f.auprc.toFixed(3) : PH}</td>
                <td className="py-2.5 font-mono">{live ? f.lift.toFixed(3) : PH}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h4 className="text-xs uppercase tracking-wide text-muted mb-3">
        Trace feature means by condition
      </h4>
      <div className="overflow-x-auto mb-2">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="border-b border-line text-left text-muted text-xs uppercase tracking-wide">
              <th className="py-2 pr-4 font-medium">Trace feature</th>
              <th className="py-2 pr-4 font-medium">Human-only</th>
              <th className="py-2 pr-4 font-medium">AI-assisted</th>
              <th className="py-2 font-medium">AI+conf</th>
            </tr>
          </thead>
          <tbody>
            {rq4Data.traceMeans.map((row) => (
              <tr key={row.feature} className="border-b border-line/60">
                <td className="py-2.5 pr-4 font-mono text-xs text-ink">{row.feature}</td>
                <td className="py-2.5 pr-4 font-mono">{live ? row.humanOnly.toFixed(2) : PH}</td>
                <td className="py-2.5 pr-4 font-mono">{live ? row.aiAssisted.toFixed(2) : PH}</td>
                <td className="py-2.5 font-mono">{live ? row.aiConf.toFixed(2) : PH}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Answer color={COND.ai_assisted} text={rq4Data.answer} />
    </div>
  );
}

function RQ5Panel() {
  const live = showLive(rq5Data.placeholder);
  const bddColor = COND.ai_assisted;
  const nuColor = '#d97706';

  function formatMetric(row: (typeof rq5Data.metrics)[number], value: number): string {
    if (row.isPercent) return `${value.toFixed(1)}%`;
    return value.toFixed(3);
  }

  function barWidth(row: (typeof rq5Data.metrics)[number], value: number): number {
    const max = row.isPercent ? 40 : 0.7;
    return Math.max((value / max) * 100, value > 0 ? 8 : 0);
  }

  return (
    <div>
      <PanelHeading title={rq5Data.title} question={rq5Data.question} />
      <p className="text-sm text-muted mb-6 leading-relaxed">
        BDD-trained SCLNScore applied to nuImages v1.0-test (
        {rq5Data.nuImagesImages.toLocaleString('en-US')} images, YOLOv8 suggestions, official 2D
        gold labels). Same export, matching, and ranking pipeline as BDD100K — no retraining on
        nuImages.
      </p>
      <h4 className="text-xs uppercase tracking-wide text-muted mb-4">
        Cross-dataset ranking (BDD-trained scorer)
      </h4>
      <div className="space-y-5 mb-2">
        {rq5Data.metrics.map((row) => (
          <div key={row.label}>
            <span className="text-sm text-muted">{row.label}</span>
            <div className="grid sm:grid-cols-2 gap-3 mt-2">
              {(
                [
                  { key: 'bdd', label: 'BDD → BDD', value: row.bddInDomain, color: bddColor },
                  { key: 'nu', label: 'BDD → nuImages', value: row.bddToNuImages, color: nuColor },
                ] as const
              ).map((series) => (
                <div key={series.key}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-muted">{series.label}</span>
                    <span className="text-ink font-mono font-medium">
                      {live ? formatMetric(row, series.value) : PH}
                    </span>
                  </div>
                  <div className="h-7 rounded-full bg-ink/[0.06] overflow-hidden">
                    <div
                      className="h-full rounded-full flex items-center justify-end pr-2 text-[11px] font-medium text-white"
                      style={{
                        width: live ? `${barWidth(row, series.value)}%` : '42%',
                        backgroundColor: live ? series.color : SKELETON,
                        color: live ? '#fff' : '#46505f',
                      }}
                    >
                      {live ? formatMetric(row, series.value) : PH}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
      <p className="text-[11px] text-muted/90 mt-4 leading-relaxed">
        Err. rate is the positive (error) rate and doubles as the AUPRC baseline for random ranking.
        Higher AUROC, AUPRC, and R@10% indicate more effective error ranking.
      </p>
      <Answer color={COND.human_only} text={rq5Data.answer} />
    </div>
  );
}

function Footer() {
  return (
    <footer className="py-10 border-t border-line">
      <div className="max-w-6xl mx-auto px-5 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <span className="w-2 h-2 rounded-full bg-accent" />
          <span className="text-sm font-medium text-ink">AILA-Bench</span>
        </div>
        <p className="text-muted text-sm text-center">
          Suggestion-Conditioned Label Noise · Anonymous Authors
        </p>
      </div>
    </footer>
  );
}

function App() {
  return (
    <div className="min-h-screen">
      <PlaceholderBanner />
      <Navigation />
      <main>
        <Hero />
        <OverviewSection />
        <DemoViewer />
        <CaseGallery />
        <ResultsExplorer />
      </main>
      <Footer />
    </div>
  );
}

export default App;
