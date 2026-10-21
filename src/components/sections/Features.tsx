"use client";

import { useRef, useState, type CSSProperties } from "react";
import SectionHead from "@/components/SectionHead";
import Slider from "@/components/Slider";
import { useFrame } from "@/lib/frame";
import styles from "./Features.module.css";

const ROWS = [
  { chip: "Default", ff: "normal", text: "Single-storey a, round dots." },
  { chip: "ss01", ff: '"ss01"', text: "Double-storey a for a, å and ä." },
  { chip: "ss02", ff: '"ss02"', text: "Square dots on i, j, ä, ö and . , : ; ! ?" },
  { chip: "ss01 + ss02", ff: '"ss01", "ss02"', text: "Both, together." },
];

/* px each row slides across the viewport (alternating direction); small enough to stay inside the cell padding on narrow screens. */
const drift = () => Math.min(48, innerWidth * 0.03);

export default function Features() {
  const [melt, setMelt] = useState(0);
  const listRef = useRef<HTMLOListElement>(null);

  useFrame(listRef, () => {
    const list = listRef.current;
    if (!list || matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const lines = list.querySelectorAll<HTMLElement>("[data-dir]");
    const amp = drift();
    lines.forEach((el) => {
      const r = el.getBoundingClientRect();
      const k = (r.top + r.height / 2 - innerHeight / 2) / innerHeight;
      el.style.transform = `translateX(${(k * amp * +el.dataset.dir!).toFixed(1)}px)`;
    });
  });

  return (
    <section id="features" className={styles.features} aria-labelledby="features-title">
      <SectionHead
        id="features-title"
        label="05 — OpenType features"
        title={<>Two sets<span className="br-t" /> of tricks.</>}
        titleClassName={styles.title}
      >
        <p>
          Stylistic sets for the way you like your a, and your dots.
          <span className={styles.notMobile}> Same text, four ways.</span>
        </p>
        <Slider
          className={styles.heat}
          label="Heat all rows (MELT)"
          valueText={`MELT ${melt}`}
          value={melt}
          onChange={(e) => setMelt(+e.target.value)}
        />
      </SectionHead>

      <ol ref={listRef} className={styles.rows} style={{ "--m": melt } as CSSProperties}>
        {ROWS.map((row, i) => (
          <li key={row.chip} className={styles.row}>
            <div className={styles.meta}>
              <span className={styles.chip}>{row.chip}</span>
              <span className={styles.desc}>{row.text}</span>
            </div>
            <div className={styles.specimen}>
              <p
                className={`${styles.line} bt`}
                style={{ "--ff": row.ff } as CSSProperties}
                data-dir={i % 2 ? 1 : -1}
                lang="nb"
              >
                Dagbladet?<span className="br-m" /> Hei, Åre!
              </p>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}
