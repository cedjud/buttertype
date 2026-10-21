import type { InputHTMLAttributes, Ref } from "react";
import styles from "./Slider.module.css";

type Props = Omit<InputHTMLAttributes<HTMLInputElement>, "type"> & {
  label: string;
  valueText: string | number;
  /** scale: "0 · value · 100" above the line (label hidden). labelled: "LABEL · value" above. inline: label, line and value on one row. */
  layout?: "scale" | "labelled" | "inline";
  inputRef?: Ref<HTMLInputElement>;
  outputRef?: Ref<HTMLOutputElement>;
};

/** 2px line with a 20px square yellow marker. */
export default function Slider({
  label, valueText, layout = "scale", inputRef, outputRef, className, min = 0, max = 100, ...rest
}: Props) {
  const output = <output ref={outputRef} className={styles.value}>{valueText}</output>;
  const input = <input ref={inputRef} type="range" min={min} max={max} className={styles.input} {...rest} />;

  if (layout === "inline") {
    return (
      <label className={`${styles.slider} ${styles.inline} ${className ?? ""}`}>
        <span className={styles.name}>{label}</span>
        {input}
        <span className={styles.inlineValue} aria-hidden="true">{output}</span>
      </label>
    );
  }

  return (
    <label className={`${styles.slider} ${className ?? ""}`}>
      {layout === "scale" ? (
        <>
          <span className="sr-only">{label}</span>
          <span className={styles.scale} aria-hidden="true">
            <span>{min}</span>{output}<span>{max}</span>
          </span>
        </>
      ) : (
        <span className={styles.scale}>
          <span>{label}</span>
          <span aria-hidden="true">{output}</span>
        </span>
      )}
      {input}
    </label>
  );
}
