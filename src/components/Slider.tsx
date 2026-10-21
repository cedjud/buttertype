import type { InputHTMLAttributes, Ref } from "react";
import styles from "./Slider.module.css";

type Props = Omit<InputHTMLAttributes<HTMLInputElement>, "type"> & {
  label: string;
  valueText: string | number;
  inputRef?: Ref<HTMLInputElement>;
  outputRef?: Ref<HTMLOutputElement>;
};

/** 2px line with a 20px square yellow marker; 0 · value · 100 scale above. */
export default function Slider({ label, valueText, inputRef, outputRef, className, min = 0, max = 100, ...rest }: Props) {
  return (
    <label className={`${styles.slider} ${className ?? ""}`}>
      <span className="sr-only">{label}</span>
      <span className={styles.scale} aria-hidden="true">
        <span>{min}</span>
        <output ref={outputRef} className={styles.value}>{valueText}</output>
        <span>{max}</span>
      </span>
      <input ref={inputRef} type="range" min={min} max={max} className={styles.input} {...rest} />
    </label>
  );
}
