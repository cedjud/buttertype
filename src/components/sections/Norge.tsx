import type { CSSProperties } from "react";
import SectionHead from "@/components/SectionHead";
import styles from "./Norge.module.css";

const GLYPHS = [
  { num: "01", m: 0, ch: "Æ", upper: "U+00C6", lower: "U+00E6", word: "ærlig", name: "Latin capital letter AE" },
  { num: "02", m: 40, ch: "Ø", upper: "U+00D8", lower: "U+00F8", word: "smør", name: "Latin capital letter O with stroke" },
  { num: "03", m: 72, ch: "Å", upper: "U+00C5", lower: "U+00E5", word: "på", name: "Latin capital letter A with ring above" },
];

export default function Norge() {
  return (
    <section id="norge" className={styles.norge} aria-labelledby="norge-title">
      <SectionHead
        id="norge-title"
        label="04 — Skrevet for Norge"
        title={<><span className={styles.big}>Æ Ø Å,</span> <span className={styles.small}>drawn from<span className="br-m" /> scratch.</span></>}
        titleClassName={styles.title}
      >
        <p className={styles.intro}>Not accents bolted on afterwards. Each Nordic letter is built into the system and melts with it.</p>
      </SectionHead>

      <ul className={styles.list}>
        {GLYPHS.map((g) => (
          <li key={g.num} className={styles.col} style={{ "--m": g.m } as CSSProperties}>
            <div className={styles.top}>
              <span>{g.num}</span>
              <span>MELT {g.m}</span>
            </div>
            <div className={styles.stage}>
              <span className={`${styles.glyph} bt`} role="img" aria-label={g.name}>{g.ch}</span>
            </div>
            <div className={styles.bottom}>
              <span>{g.upper}<span className={styles.lower}> · {g.lower}</span></span>
              <span className={`${styles.word} bt`} lang="nb">{g.word}</span>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
