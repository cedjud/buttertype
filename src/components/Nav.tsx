"use client";

import { useEffect, useRef, useState } from "react";
import { MOODS } from "@/lib/axes";
import { useFrame } from "@/lib/frame";
import { setMood, useMood } from "@/lib/mood";
import styles from "./Nav.module.css";

/* `wide` links only fit the desktop bar; tablet drops them. */
const LINKS = [
  { href: "#axes", label: "Axes" },
  { href: "#norge", label: "Æ Ø Å" },
  { href: "#glyphs", label: "Glyphs" },
  { href: "#tester", label: "Tester" },
  { href: "#specs", label: "Specs", wide: true },
];

const MENU_LINKS = [
  { href: "#melt", label: "Melt" },
  { href: "#axes", label: "Axes" },
  { href: "#norge", label: "Æ Ø Å" },
  { href: "#glyphs", label: "Glyphs" },
  { href: "#tester", label: "Tester" },
  { href: "#inuse", label: "In use" },
  { href: "#specs", label: "Specs" },
  { href: "#licence", label: "Licence" },
];

function MoodButtons({ className }: { className?: string }) {
  const mood = useMood();
  return (
    <>
      {MOODS.map(({ name }) => (
        <button
          key={name}
          type="button"
          className={className}
          aria-pressed={mood === name}
          onClick={() => setMood(name)}
        >
          {name}
        </button>
      ))}
    </>
  );
}

export default function Nav() {
  const barRef = useRef<HTMLSpanElement>(null);
  const menuBtnRef = useRef<HTMLButtonElement>(null);
  const closeBtnRef = useRef<HTMLButtonElement>(null);
  const [active, setActive] = useState<string | null>(null);
  const [open, setOpen] = useState(false);

  /* Scroll progress bar */
  useFrame(null, () => {
    const bar = barRef.current;
    if (!bar) return;
    const max = Math.max(1, document.documentElement.scrollHeight - innerHeight);
    bar.style.transform = `scaleX(${(scrollY / max).toFixed(4)})`;
  }, { always: true });

  /* Scroll-spy */
  useEffect(() => {
    const io = new IntersectionObserver(
      (entries) => entries.forEach((e) => { if (e.isIntersecting) setActive("#" + e.target.id); }),
      { rootMargin: "-45% 0px -50% 0px" },
    );
    MENU_LINKS.forEach(({ href }) => {
      const el = document.querySelector(href);
      if (el) io.observe(el);
    });
    return () => io.disconnect();
  }, []);

  /* Mobile menu: focus, Escape, scroll lock */
  useEffect(() => {
    if (!open) return;
    const root = document.documentElement;
    const menuBtn = menuBtnRef.current;
    root.style.overflow = "hidden";
    closeBtnRef.current?.focus();
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") setOpen(false); };
    addEventListener("keydown", onKey);
    return () => {
      root.style.overflow = "";
      removeEventListener("keydown", onKey);
      menuBtn?.focus();
    };
  }, [open]);

  const close = () => setOpen(false);

  return (
    <nav className={styles.nav} aria-label="Main">
      <a href="#top" className={`${styles.logo} bt bt-hover`} aria-label="BT Smör, back to top">BT Smör</a>

      <div className={styles.mood} role="group" aria-label="Mood">
        <span className={styles.moodLabel} aria-hidden="true">Mood</span>
        <MoodButtons className={styles.cell} />
      </div>

      <ul className={styles.links}>
        {LINKS.map(({ href, label, wide }) => (
          <li key={href} className={wide ? styles.wide : undefined}>
            <a href={href} className={styles.cell} aria-current={active === href ? "location" : undefined}>{label}</a>
          </li>
        ))}
        <li>
          <a href="#licence" className={`${styles.cell} ${styles.licence}`}>Licence</a>
        </li>
      </ul>

      <button
        ref={menuBtnRef}
        type="button"
        className={styles.menuBtn}
        aria-expanded={open}
        aria-controls="mobile-menu"
        onClick={() => setOpen(true)}
      >
        Menu
      </button>

      <span ref={barRef} className={styles.bar} aria-hidden="true" />

      {open && (
        <div id="mobile-menu" className={styles.menu} role="dialog" aria-modal="true" aria-label="Menu">
          <div className={styles.menuHead}>
            <span className={`${styles.menuLogo} bt`}>BT Smör</span>
            <button ref={closeBtnRef} type="button" className={styles.menuClose} onClick={close}>Close ×</button>
          </div>
          <ol className={styles.menuLinks}>
            {MENU_LINKS.map(({ href, label }, i) => (
              <li key={href}>
                <a href={href} onClick={close}>
                  <span className={styles.menuNum}>{String(i + 1).padStart(2, "0")}</span>
                  <span className={`${styles.menuName} bt`}>{label}</span>
                  <span className={styles.menuArrow} aria-hidden="true">→</span>
                </a>
              </li>
            ))}
          </ol>
          <div className={styles.menuMood} role="group" aria-label="Mood">
            <span aria-hidden="true">Mood</span>
            <MoodButtons />
          </div>
          <a href="#tester" className={styles.menuCta} onClick={close}>
            <span>Test the font</span><span aria-hidden="true">→</span>
          </a>
        </div>
      )}
    </nav>
  );
}
