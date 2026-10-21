"use client";

import { useEffect, useRef, useState, type CSSProperties } from "react";
import Slider from "@/components/Slider";
import { stageName } from "@/lib/axes";
import styles from "./Tester.module.css";

const PRESETS = [
  { name: "Norwegian pangram", text: "Vår søte smør smelter på brødskiva" },
  { name: "Headline", text: "Smør smelter" },
  { name: "Uppercase", text: "ABCDEFGHIJKLMNOPQRSTUVWXYZ ÆØÅ" },
  { name: "Lowercase", text: "abcdefghijklmnopqrstuvwxyz æøå" },
  { name: "Figures", text: "0123456789 (+–=) ?!" },
];

const THEMES = [
  { name: "Black on yellow", bg: "var(--yellow)", fg: "var(--black)" },
  { name: "Yellow on black", bg: "var(--black)", fg: "var(--yellow)" },
  { name: "Black on white", bg: "var(--white)", fg: "var(--black)" },
  { name: "White on black", bg: "var(--black)", fg: "var(--white)" },
];

const ALIGNS = [
  { value: "left", label: "Left" },
  { value: "center", label: "Centre" },
  { value: "right", label: "Right" },
] as const;

const DEFAULTS = { size: 150, tracking: 0, leading: 1.05, align: "left" as (typeof ALIGNS)[number]["value"], m: 0, b: 100, s: 100, ss01: false, ss02: false, theme: 0 };

/* Smaller starting size where the stage is narrower. */
const defaultSize = () => (innerWidth < 640 ? 56 : innerWidth < 1024 ? 96 : DEFAULTS.size);

export default function Tester() {
  const [preset, setPreset] = useState(0);
  const [size, setSize] = useState(DEFAULTS.size);
  const [tracking, setTracking] = useState(DEFAULTS.tracking);
  const [leading, setLeading] = useState(DEFAULTS.leading);
  const [align, setAlign] = useState(DEFAULTS.align);
  const [m, setM] = useState(DEFAULTS.m);
  const [b, setB] = useState(DEFAULTS.b);
  const [s, setS] = useState(DEFAULTS.s);
  const [ss01, setSs01] = useState(DEFAULTS.ss01);
  const [ss02, setSs02] = useState(DEFAULTS.ss02);
  const [theme, setTheme] = useState(DEFAULTS.theme);
  const [animating, setAnimating] = useState(false);
  const textRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const z = defaultSize();
    // eslint-disable-next-line react-hooks/set-state-in-effect -- viewport is only known on the client
    if (z !== DEFAULTS.size) setSize(z);
  }, []);

  /* "Animate MELT": 50 − 50·cos(t), one cycle every 4s. */
  useEffect(() => {
    if (!animating) return;
    let raf = 0;
    const t0 = performance.now();
    const from = Math.acos(1 - m / 50); // start the wave from the current value
    const loop = (t: number) => {
      setM(Math.round(50 - 50 * Math.cos(from + ((t - t0) / 4000) * Math.PI * 2)));
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(raf);
    // eslint-disable-next-line react-hooks/exhaustive-deps -- only (re)start on toggle
  }, [animating]);

  const choosePreset = (i: number) => {
    setPreset(i);
    if (textRef.current) textRef.current.textContent = PRESETS[i].text;
  };

  const reset = () => {
    setAnimating(false);
    setSize(defaultSize());
    setTracking(DEFAULTS.tracking);
    setLeading(DEFAULTS.leading);
    setAlign(DEFAULTS.align);
    setM(DEFAULTS.m);
    setB(DEFAULTS.b);
    setS(DEFAULTS.s);
    setSs01(DEFAULTS.ss01);
    setSs02(DEFAULTS.ss02);
    setTheme(DEFAULTS.theme);
    choosePreset(0);
  };

  const ff = [ss01 && '"ss01"', ss02 && '"ss02"'].filter(Boolean).join(", ");
  const th = THEMES[theme];

  const code = [
    `font-family: "BT Smör";`,
    `font-size: ${size}px;`,
    `letter-spacing: ${tracking.toFixed(2)}em;`,
    `line-height: ${leading.toFixed(2)};`,
    `font-variation-settings: "MELT" ${m}, "BUBL" ${b}, "SLMP" ${s};`,
    ff && `font-feature-settings: ${ff};`,
  ].filter(Boolean).join("\n");

  return (
    <section id="tester" className={styles.tester} aria-labelledby="tester-title">
      <div className={styles.head}>
        <h2 id="tester-title" className={styles.headTitle}>07 — Type tester</h2>
        <span className={styles.headNote}>Every control is live</span>
      </div>

      <div className={styles.body}>
        <div className={styles.stage} style={{ "--stage-bg": th.bg, "--stage-fg": th.fg } as CSSProperties}>
          <div className={styles.stageMeta} aria-hidden="true">
            <span>BT Smör · Variable</span>
            <span>{size} px · {stageName(m)}</span>
          </div>
          <div className={styles.textWrap}>
            <div
              ref={textRef}
              className={`${styles.text} bt`}
              contentEditable
              suppressContentEditableWarning
              spellCheck={false}
              role="textbox"
              aria-multiline="true"
              aria-label="Sample text, editable"
              lang="nb"
              style={{
                "--m": m, "--b": b, "--s": s, "--ff": ff || "normal",
                fontSize: size, letterSpacing: `${tracking}em`, lineHeight: leading, textAlign: align,
              } as CSSProperties}
            >
              {PRESETS[0].text}
            </div>
          </div>
          <pre className={styles.code} aria-label="CSS for the current settings">{code}</pre>
        </div>

        <div className={styles.controls}>
          <div className={styles.group}>
            <label className={`${styles.ctl} ${styles.ctlRow}`}>
              <span>Text</span>
              <span className={styles.selectWrap}>
                <select className={styles.select} value={preset} onChange={(e) => choosePreset(+e.target.value)}>
                  {PRESETS.map((p, i) => <option key={p.name} value={i}>{p.name}</option>)}
                </select>
                <span aria-hidden="true"> ▾</span>
              </span>
            </label>
            <div className={`${styles.ctl} ${styles.tall}`}>
              <Slider layout="labelled" label="Size" valueText={`${size} px`} min={24} max={320} value={size} onChange={(e) => setSize(+e.target.value)} />
            </div>
            <div className={styles.ctl}>
              <Slider layout="inline" label="Tracking" valueText={`${tracking.toFixed(2)}em`} min={-0.1} max={0.2} step={0.01} value={tracking} onChange={(e) => setTracking(+e.target.value)} />
            </div>
            <div className={styles.ctl}>
              <Slider layout="inline" label="Leading" valueText={leading.toFixed(2)} min={0.8} max={1.6} step={0.01} value={leading} onChange={(e) => setLeading(+e.target.value)} />
            </div>
            <div className={`${styles.ctl} ${styles.tall}`} role="group" aria-labelledby="tester-align">
              <span id="tester-align" className={styles.ctlLabel}>Alignment</span>
              <div className={styles.segments}>
                {ALIGNS.map((a) => (
                  <button key={a.value} type="button" aria-pressed={align === a.value} onClick={() => setAlign(a.value)}>{a.label}</button>
                ))}
              </div>
            </div>
          </div>

          <div className={styles.group}>
            <div className={`${styles.ctl} ${styles.tall}`}>
              <Slider layout="labelled" label="MELT" valueText={m} value={m} onChange={(e) => { setAnimating(false); setM(+e.target.value); }} />
            </div>
            <div className={`${styles.ctl} ${styles.tall}`}>
              <Slider layout="labelled" label="BUBL" valueText={b} value={b} onChange={(e) => setB(+e.target.value)} />
            </div>
            <div className={`${styles.ctl} ${styles.tall}`}>
              <Slider layout="labelled" label="SLMP" valueText={s} value={s} onChange={(e) => setS(+e.target.value)} />
            </div>
            <div className={`${styles.ctl} ${styles.tall}`} role="group" aria-labelledby="tester-features">
              <span id="tester-features" className={styles.ctlLabel}>Features</span>
              <div className={styles.chips}>
                <button type="button" aria-pressed={ss01} onClick={() => setSs01(!ss01)}>ss01</button>
                <button type="button" aria-pressed={ss02} onClick={() => setSs02(!ss02)}>ss02</button>
              </div>
            </div>
            <div className={`${styles.ctl} ${styles.tall}`} role="group" aria-labelledby="tester-theme">
              <span id="tester-theme" className={styles.ctlLabel}>Theme</span>
              <div className={styles.swatches}>
                {THEMES.map((t, i) => (
                  <button
                    key={t.name}
                    type="button"
                    className="bt"
                    aria-label={t.name}
                    aria-pressed={theme === i}
                    style={{ background: t.bg, color: t.fg }}
                    onClick={() => setTheme(i)}
                  >
                    A
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className={styles.actions}>
            <button type="button" aria-pressed={animating} onClick={() => setAnimating(!animating)}>
              {animating ? "Stop" : "Animate MELT"}
            </button>
            <button type="button" onClick={reset}>Reset</button>
          </div>
        </div>
      </div>
    </section>
  );
}
