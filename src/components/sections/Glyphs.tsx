"use client";

import { useState, type CSSProperties } from "react";
import SectionHead from "@/components/SectionHead";
import Slider from "@/components/Slider";
import { GLYPH_GROUPS, codePoint, glyphName, hasSs01, hasSs02 } from "@/lib/glyphs";
import styles from "./Glyphs.module.css";

export default function Glyphs() {
  const [sel, setSel] = useState("Å");
  const [m, setM] = useState(0);
  const [b, setB] = useState(100);
  const [s, setS] = useState(100);
  const [ss01, setSs01] = useState(false);
  const [ss02, setSs02] = useState(false);

  const can01 = hasSs01(sel), can02 = hasSs02(sel);
  const on01 = can01 && ss01, on02 = can02 && ss02;
  const ff = [on01 && '"ss01"', on02 && '"ss02"'].filter(Boolean).join(", ") || "normal";

  return (
    <section id="glyphs" className={styles.glyphs} aria-labelledby="glyphs-title">
      <SectionHead
        id="glyphs-title"
        label="06 — The character set"
        title={<>Every<span className="br-m" /> glyph.</>}
        titleClassName={styles.title}
      >
        <p>
          Every character in the family<span className={styles.notMobile}>, from capitals and figures to the Nordic letters</span>.{" "}
          <span className={styles.notMobile}>Select</span><span className={styles.onlyMobile}>Tap</span> one to inspect it.
        </p>
      </SectionHead>

      <div className={styles.body}>
        <div className={styles.inspector}>
          <div className={styles.big} aria-live="polite">
            <span
              className={`${styles.bigGlyph} bt`}
              style={{ "--m": m, "--b": b, "--s": s, "--ff": ff } as CSSProperties}
              aria-hidden="true"
            >
              {sel}
            </span>
            <span className="sr-only">{glyphName(sel)} selected</span>
          </div>
          <div className={styles.details}>
            <p className={styles.name}>{glyphName(sel)}</p>
            <p className={styles.code}><span>Unicode</span><span>{codePoint(sel)}</span></p>
            <Slider className={styles.row} layout="labelled" label="MELT" valueText={m} value={m} onChange={(e) => setM(+e.target.value)} />
            <Slider className={styles.row} layout="labelled" label="BUBL" valueText={b} value={b} onChange={(e) => setB(+e.target.value)} />
            <Slider className={styles.row} layout="labelled" label="SLMP" valueText={s} value={s} onChange={(e) => setS(+e.target.value)} />
            <div className={styles.chips} role="group" aria-label="Stylistic sets">
              <button type="button" className={styles.chip} aria-pressed={on01} disabled={!can01} onClick={() => setSs01(!ss01)}>ss01</button>
              <button type="button" className={styles.chip} aria-pressed={on02} disabled={!can02} onClick={() => setSs02(!ss02)}>ss02</button>
              {!can01 && !can02 && <span className={styles.none}>No alternates</span>}
            </div>
          </div>
        </div>

        <div className={styles.grid}>
          {GLYPH_GROUPS.map((g) => (
            <div key={g.name} role="group" aria-labelledby={`glyph-group-${g.name}`}>
              <h3 id={`glyph-group-${g.name}`} className={styles.groupHead}>
                <span>{g.name}</span><span>{g.chars.length}</span>
              </h3>
              <div className={styles.cells}>
                {g.chars.map((c) => (
                  <button
                    key={c}
                    type="button"
                    className={`${styles.cell} bt bt-hover`}
                    aria-pressed={c === sel}
                    aria-label={glyphName(c)}
                    onClick={() => setSel(c)}
                  >
                    <span aria-hidden="true">{c}</span>
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
