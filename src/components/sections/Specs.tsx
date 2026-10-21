import SectionHead from "@/components/SectionHead";
import styles from "./Specs.module.css";

const METRICS = [
  { value: "1000", label: "Units per em" },
  { value: "720", label: "Cap height" },
  { value: "540", label: "x-height" },
  { value: "−200", label: "Descender" },
];

type Table = { title: string; cols: string[]; widths: string[]; rows: string[][] };

const LEFT: Table[] = [
  {
    title: "Axes",
    cols: ["Axis", "Name", "Min", "Default", "Max"],
    widths: ["70px", "auto", "48px", "78px", "48px"],
    rows: [["MELT", "Meltiness", "0", "0", "100"], ["BUBL", "Bubbles", "0", "100", "100"], ["SLMP", "Slump", "0", "100", "100"]],
  },
  {
    title: "Features",
    cols: ["Feature", "What it does"],
    widths: ["78px", "auto"],
    rows: [["ss01", "Double-storey a, å, ä"], ["ss02", "Square dots on i j ä ö and . , : ; ! ?"]],
  },
];

const RIGHT: Table[] = [
  {
    title: "Named instances",
    cols: ["Instance", "MELT", "BUBL", "SLMP"],
    widths: ["auto", "64px", "64px", "64px"],
    rows: [
      ["Solid", "0", "100", "100"], ["Soft", "33", "100", "100"], ["Gooey", "66", "100", "100"],
      ["Puddle", "100", "100", "100"], ["Calm Puddle", "100", "40", "20"], ["Hot Pan", "100", "100", "0"],
    ],
  },
  {
    title: "Coverage",
    cols: ["Area", "Detail"],
    widths: ["88px", "auto"],
    rows: [["Latin", "A–Z, a–z, figures, basic punctuation"], ["Nordic", "Æ Ø Å æ ø å Ä Ö É ä ö é"], ["Formats", "Variable TTF, plus static Solid and Puddle"]],
  },
];

function SpecTable({ t }: { t: Table }) {
  return (
    <table className={styles.table}>
      <caption className={styles.caption}>{t.title}</caption>
      {/* Edge columns also carry the gutter padding, so add it to their widths. */}
      <colgroup>
        {t.widths.map((w, i) => {
          const edge = i === 0 || i === t.widths.length - 1;
          return <col key={i} style={{ width: w === "auto" ? undefined : edge ? `calc(${w} + var(--gutter))` : w }} />;
        })}
      </colgroup>
      <thead>
        <tr>{t.cols.map((c) => <th key={c} scope="col">{c}</th>)}</tr>
      </thead>
      <tbody>
        {t.rows.map((r) => (
          <tr key={r[0]}>{r.map((c, i) => (i === 0 ? <th key={i} scope="row">{c}</th> : <td key={i}>{c}</td>))}</tr>
        ))}
      </tbody>
    </table>
  );
}

export default function Specs() {
  return (
    <section id="specs" className={styles.specs} aria-labelledby="specs-title">
      <SectionHead
        id="specs-title"
        label="09 — Specifications"
        title={<>The<span className="br-m" /> details.</>}
        titleClassName={styles.title}
      >
        <p>Metrics, axes, instances, features and coverage at a glance.</p>
      </SectionHead>

      <dl className={styles.metrics}>
        {METRICS.map((m) => (
          <div key={m.label} className={styles.metric}>
            <dt className={styles.metricLabel}>{m.label}</dt>
            <dd className={`${styles.metricValue} bt`}>{m.value}</dd>
          </div>
        ))}
      </dl>

      <div className={styles.tables}>
        <div className={styles.col}>{LEFT.map((t) => <SpecTable key={t.title} t={t} />)}</div>
        <div className={styles.col}>{RIGHT.map((t) => <SpecTable key={t.title} t={t} />)}</div>
      </div>
    </section>
  );
}
