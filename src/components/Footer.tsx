"use client";

import { useRef } from "react";
import { clamp, setAxes } from "@/lib/axes";
import { useFrame } from "@/lib/frame";
import styles from "./Footer.module.css";

export default function Footer() {
  const footRef = useRef<HTMLElement>(null);
  const wordRef = useRef<HTMLDivElement>(null);

  /* MELT follows how far the footer has come into view. */
  useFrame(footRef, () => {
    const foot = footRef.current, word = wordRef.current;
    if (!foot || !word) return;
    const r = foot.getBoundingClientRect();
    setAxes(word, clamp((innerHeight - r.top) / (r.height * 0.9)) * 100, 100, 100);
  }, { margin: "0px" });

  return (
    <footer ref={footRef} id="contact" className={styles.footer}>
      <div className={styles.top}>
        <div className={styles.lede}>
          <p>Questions, licences, custom work? Get in touch and we’ll warm up the pan.</p>
          {/* PLACEHOLDER: contact details were not supplied in the handoff. */}
          <p className={styles.placeholder}>[Contact details — to be supplied by client]</p>
        </div>
        <p className={styles.label}>BT Smör<br />Variable typeface<br />2026</p>
      </div>

      <div className={styles.wordWrap} aria-hidden="true">
        <div ref={wordRef} className={`${styles.word} bt`}>Smør</div>
      </div>

      <div className={styles.legal}>
        {/* PLACEHOLDER: foundry name and legal copy not supplied. */}
        <span>© 2026 BT</span>
        <a href="#top">Back to top ↑</a>
      </div>
    </footer>
  );
}
