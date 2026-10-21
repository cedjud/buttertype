"use client";

import { useRef } from "react";
import SectionHead from "@/components/SectionHead";
import Slider from "@/components/Slider";
import { clamp, setAxes } from "@/lib/axes";
import { useFrame } from "@/lib/frame";
import styles from "./Axes.module.css";

type Tag = "MELT" | "BUBL" | "SLMP";

const AXES: { tag: Tag; name: string; def: number; value: number; theme: string; text: string; textWide?: string }[] = [
  {
    tag: "MELT", name: "Meltiness", def: 0, value: 70, theme: "yellow",
    text: "From razor-sharp corners to a full puddle. Terminals round off, drips form, letters sink.",
  },
  {
    tag: "BUBL", name: "Bubbles", def: 100, value: 100, theme: "black",
    text: "Foam on the puddle, bubbles rising, tiny pan-sizzle droplets. Shown at MELT 100.",
  },
  {
    tag: "SLMP", name: "Slump", def: 100, value: 20, theme: "white",
    text: "How far the letters lean, droop and sink. Dial it down and a melted line stays readable.",
    textWide: " Shown at MELT 100.",
  },
];

/* Each demo isolates one axis: MELT alone; BUBL at MELT 100; SLMP at MELT 100 / BUBL 40. */
function apply(tag: Tag, el: HTMLElement, v: number) {
  if (tag === "MELT") setAxes(el, v, 100, 100);
  else if (tag === "BUBL") setAxes(el, 100, v, 100);
  else setAxes(el, 100, 40, v);
}

function AxisColumn({ axis }: { axis: (typeof AXES)[number] }) {
  const colRef = useRef<HTMLLIElement>(null);
  const demoRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const outputRef = useRef<HTMLOutputElement>(null);
  const auto = useRef(true);

  /* Until touched, the slider drifts with the column's position in the viewport. */
  useFrame(colRef, () => {
    const col = colRef.current, input = inputRef.current, demo = demoRef.current, out = outputRef.current;
    if (!col || !input || !demo || !out) return;
    if (auto.current) {
      const r = col.getBoundingClientRect();
      const k = clamp(1 - (r.top + r.height / 2) / innerHeight);
      input.value = String(Math.round(clamp(k / 0.75) * 100));
    }
    const v = +input.value;
    const txt = String(v);
    if (out.textContent !== txt) out.textContent = txt;
    apply(axis.tag, demo, v);
  });

  return (
    <li ref={colRef} className={styles.axis}>
      <div className={styles.axisHead}>
        <h3 className={`${styles.tag} bt`}>{axis.tag}</h3>
        <p className={styles.range}>
          <span>{axis.name}</span>
          <span>0–100<span className={styles.sep}> · </span></span>
          <span>default {axis.def}</span>
        </p>
      </div>
      <div className={`${styles.field} ${styles[axis.theme]}`}>
        <div ref={demoRef} className={`${styles.word} bt`} aria-hidden="true">Smør</div>
      </div>
      <div className={styles.body}>
        <p className={styles.text}>
          {axis.text}
          {axis.textWide && <span className={styles.wideOnly}>{axis.textWide}</span>}
        </p>
        <div className={styles.control}>
          <Slider
            label={`${axis.tag} (${axis.name})`}
            valueText={axis.value}
            inputRef={inputRef}
            outputRef={outputRef}
            defaultValue={axis.value}
            onInput={() => { auto.current = false; }}
            onPointerDown={() => { auto.current = false; }}
          />
        </div>
      </div>
    </li>
  );
}

export default function Axes() {
  return (
    <section id="axes" className={styles.axes} aria-labelledby="axes-title">
      <SectionHead
        id="axes-title"
        label="03 — Three axes, one block of butter"
        title={<>Dial it<span className="br-m" /> in.</>}
        titleClassName={styles.title}
      >
        <p>Every letter is built from overlapping strokes, so the font morphs smoothly between a crisp, sharp-cornered face and a bubbling puddle.</p>
      </SectionHead>
      <ul className={styles.list}>
        {AXES.map((a) => <AxisColumn key={a.tag} axis={a} />)}
      </ul>
    </section>
  );
}
