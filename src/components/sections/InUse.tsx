"use client";

import { useState, type CSSProperties, type ReactNode } from "react";
import SectionHead from "@/components/SectionHead";
import styles from "./InUse.module.css";

/* Mock content for the mockups — prices, venue and date are placeholders, not facts. */
const MENU = [
  { name: "Smørbrød", price: "129,–", ss01: true },
  { name: "Brunost", price: "49,–", ss01: false },
  { name: "Rømmegrøt", price: "119,–", ss01: true },
  { name: "Lefse", price: "39,–", ss01: false },
];

const POSTER = [
  { text: "Smør", m: 0, size: 36 },
  { text: "smelter", m: 34, size: 24.5 },
  { text: "på", m: 68, size: 36 },
  { text: "brødskiva", m: 100, size: 17.8 },
];

const STICKERS = [
  { text: "100% Smør", theme: "yellow", size: 38 },
  { text: "Æ Ø Å", theme: "black", size: 40 },
  { text: "Melt me", theme: "white", size: 42 },
  { text: "Varm!", theme: "yellow", size: 46 },
  { text: "Smør", theme: "blackWhite", size: 48 },
  { text: "Brunost", theme: "white", size: 30, narrowOnly: true },
];

/** A mockup that melts on hover (pointer devices) and toggles on tap/click/Enter. */
function Mock({ label, className, children }: { label: string; className: string; children: ReactNode }) {
  const [hot, setHot] = useState(false);
  return (
    <button
      type="button"
      className={`${styles.mock} ${className}`}
      aria-pressed={hot}
      aria-label={`${label} — melt`}
      onClick={() => setHot(!hot)}
    >
      {children}
    </button>
  );
}

const v = (cold: number, hot: number) => ({ "--cold": cold, "--hot": hot }) as CSSProperties;

export default function InUse() {
  return (
    <section id="inuse" className={styles.inuse} aria-labelledby="inuse-title">
      <SectionHead
        id="inuse-title"
        label="08 — In the wild"
        title={<><span className={styles.hoverWord}>Hover</span><span className={styles.tapWord}>Tap</span> to<span className="br-m" /> melt.</>}
        titleClassName={styles.title}
      >
        <p className={styles.intro}>Packaging, posters, menus and stickers, set in one family from sharp to melted.</p>
      </SectionHead>

      <div className={styles.grid}>
        <Mock label="Butter wrapper" className={styles.wrapper}>
          <span className={styles.wrapperBody}>
            <span className={styles.meta}><span>Usaltet</span><span>Netto 250 g</span></span>
            <span className={`${styles.wrapperWord} ${styles.w} bt`} style={v(0, 100)} lang="nb">Smør</span>
            <span aria-hidden="true" />
          </span>
          <span className={styles.wrapperBand}><span>Kjøles</span><span>Unsalted butter</span></span>
        </Mock>

        <Mock label="Exhibition poster" className={styles.poster}>
          <span className={styles.meta}><span>Utstilling</span><span>Oslo · Aug<span className={styles.notTablet}>ust</span> 2026</span></span>
          <span className={`${styles.posterLines} bt`} lang="nb">
            {POSTER.map((l, i) => (
              <span
                key={l.text}
                className={styles.w}
                style={{ ...v(l.m, 100), fontSize: `${l.size}cqi`, transitionDelay: `${i * 90}ms` } as CSSProperties}
              >
                {l.text}
              </span>
            ))}
          </span>
          <span className={`${styles.meta} ${styles.posterFoot}`}>
            <span><span className={styles.hoverWord}>Hover</span><span className={styles.tapWord}>Tap</span> to heat</span>
            <span aria-hidden="true">↓</span>
          </span>
        </Mock>

        <Mock label="Menu card" className={styles.menu}>
          <span className={`${styles.menuTitle} ${styles.w} bt`} style={{ ...v(0, 70), "--ff": '"ss01"' } as CSSProperties} lang="nb">Meny</span>
          <span className={styles.menuList}>
            {MENU.map((it, i) => (
              <span key={it.name} className={styles.menuItem}>
                <span
                  className={`${styles.menuName} ${styles.w} bt`}
                  style={{ ...v(0, 45), "--ff": it.ss01 ? '"ss01"' : "normal", transitionDelay: `${(i + 1) * 70}ms` } as CSSProperties}
                  lang="nb"
                >
                  {it.name}
                </span>
                <span className={styles.price}>{it.price}</span>
              </span>
            ))}
          </span>
        </Mock>

        <ul className={styles.stickers}>
          {STICKERS.map((s) => (
            <li key={s.text} className={s.narrowOnly ? styles.narrowOnly : undefined}>
              <Mock label={`Sticker “${s.text}”`} className={`${styles.sticker} ${styles[s.theme]}`}>
                <span className={`${styles.w} bt`} style={{ ...v(0, 100), "--sz": `${s.size}px` } as CSSProperties} lang="nb">{s.text}</span>
              </Mock>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
