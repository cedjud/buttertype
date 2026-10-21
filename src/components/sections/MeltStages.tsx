import type { CSSProperties } from "react";
import styles from "./MeltStages.module.css";

const STAGES = [
  {
    num: "01", name: "Solid", m: 0,
    text: "Sharp as a fresh-cut block. Flat-cut terminals, mitred corners, and feet cut dead level",
    textWide: " on A, V, W and X.",
  },
  {
    num: "02", name: "Soft", m: 33,
    text: "Corners start to give. Terminals round off and the first drips form under crossbars",
    textWide: " and curves.",
  },
  {
    num: "03", name: "Gooey", m: 66,
    text: "Letters lean, droop and sink. Drips run, droplets fall, and bubbles begin to rise.",
    textWide: "",
  },
  {
    num: "04", name: "Puddle", m: 100,
    text: "Everything ends in the pool. One continuous puddle runs under the whole line",
    textWide: ", and the foam sits on top.",
  },
];

export default function MeltStages() {
  return (
    <section id="melt" className={styles.melt} aria-labelledby="melt-title">
      <div className={styles.head}>
        <h2 id="melt-title" className={styles.headCell}>02 — MELT axis</h2>
        <div className={`${styles.headCell} ${styles.headMid}`}>
          <span className={styles.notMobile}>Four stages · one variable font</span>
          <span className={styles.onlyMobile}>4 stages</span>
        </div>
        <div className={`${styles.headCell} ${styles.headEnd}`}>Corners · terminals · drips · puddle</div>
      </div>

      <ol className={styles.rows}>
        {STAGES.map((st) => (
          <li key={st.num} className={styles.row}>
            <div className={styles.meta}>
              <span>{st.num}</span>
              <span className={`${styles.name} bt`}>{st.name}</span>
              <span>MELT {st.m}</span>
            </div>
            <div className={styles.specimen} style={{ "--m": st.m } as CSSProperties}>
              <div className={`${styles.word} bt specimen`} aria-hidden="true">Smør</div>
            </div>
            <p className={styles.text}>
              {st.text}
              <span className={styles.notMobile}>{st.textWide}</span>
              <span className={styles.onlyMobile}>{st.textWide ? "." : ""}</span>
            </p>
          </li>
        ))}
      </ol>
    </section>
  );
}
