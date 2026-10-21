"use client";

import { useMemo, useRef } from "react";
import GuideLines from "@/components/GuideLines";
import { clamp, pad3, setAxes, stageName } from "@/lib/axes";
import { useFrame } from "@/lib/frame";
import { moodMelt } from "@/lib/mood";
import styles from "./Hero.module.css";

const BUBBLE_COUNT = 18;

/* Deterministic pseudo-random so server and client render the same bubbles. */
function seeded(i: number) {
  const x = Math.sin(i * 9301 + 49297) * 233280;
  return x - Math.floor(x);
}

export default function Hero() {
  const sectionRef = useRef<HTMLElement>(null);
  const pinRef = useRef<HTMLDivElement>(null);
  const wordRef = useRef<HTMLHeadingElement>(null);
  const readoutRef = useRef<HTMLSpanElement>(null);
  const bubblesRef = useRef<HTMLDivElement>(null);

  const bubbles = useMemo(
    () => Array.from({ length: BUBBLE_COUNT }, (_, i) => ({
      size: Math.round(14 + seeded(i) * 70),
      left: Math.round(2 + seeded(i + 40) * 94),
      top: Math.round(35 + seeded(i + 80) * 70),
      speed: 0.25 + seeded(i + 120) * 1.15,
    })),
    [],
  );

  useFrame(sectionRef, () => {
    const sec = sectionRef.current, pin = pinRef.current, word = wordRef.current;
    if (!sec || !pin || !word) return;

    const navH = parseFloat(getComputedStyle(pin).top) || 0;
    const r = sec.getBoundingClientRect();
    const p = clamp((navH - r.top) / Math.max(1, r.height - pin.offsetHeight));
    const m = Math.max(moodMelt(), clamp(p / 0.9) * 100);

    setAxes(word, m, 100, 100);

    const txt = `MELT ${pad3(m)} · ${stageName(m)}`;
    const readout = readoutRef.current;
    if (readout && readout.textContent !== txt) readout.textContent = txt;

    const op = (clamp((m - 25) / 40) * 0.85).toFixed(2);
    const kids = bubblesRef.current?.children;
    if (kids) {
      for (let i = 0; i < kids.length; i++) {
        const el = kids[i] as HTMLElement;
        el.style.opacity = op;
        el.style.transform = `translateY(${(-p * bubbles[i].speed * innerHeight * 1.1).toFixed(1)}px)`;
      }
    }
  });

  return (
    <header ref={sectionRef} id="top" className={styles.hero}>
      <div ref={pinRef} className={styles.pin}>
        <GuideLines />

        <div className={styles.meta}>
          <div className={styles.metaCell}>
            <span className={styles.desk}>BT Smör<br />Variable typeface</span>
            <span className={styles.mob}>Variable typeface<br />3 axes · 108 glyphs</span>
          </div>
          <div className={`${styles.metaCell} ${styles.desk}`}>Version 2.0 · 2026<br />Drawn for Norwegian</div>
          <div className={`${styles.metaCell} ${styles.desk}`}>3 axes · 108 glyphs<br />2 stylistic sets</div>
          <div className={`${styles.metaCell} ${styles.readout}`}>
            BUBL 100 · SLMP 100
            <span ref={readoutRef} className={styles.readoutValue}>MELT 000 · Solid</span>
          </div>
        </div>

        <div className={styles.stage}>
          <div ref={bubblesRef} className={styles.bubbles} aria-hidden="true">
            {bubbles.map((b, i) => (
              <i key={i} style={{ width: b.size, height: b.size, left: `${b.left}%`, top: `${b.top}%` }} />
            ))}
          </div>
          <h1 ref={wordRef} className={`${styles.word} bt`}>
            <span>BT</span> <span>Smör</span>
          </h1>
        </div>

        <div className={styles.foot}>
          <p className={styles.copy}>
            A butter-inspired variable typeface in the spirit of GT Walsheim and Otto Baumberger’s poster lettering.{" "}
            <span className={styles.desk}>Razor-sharp</span><span className={styles.mob}>Sharp</span> when cold. Gooey when warm. Drawn for Norwegian.
          </p>
          <div className={styles.hint}>
            <span className={styles.desk}>Scroll to turn up the heat ↓</span>
            <span className={styles.mob}>Scroll to melt ↓</span>
          </div>
          <a href="#tester" className={styles.cta}>Test the font →</a>
        </div>
      </div>
    </header>
  );
}
