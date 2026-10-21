import styles from "./GuideLines.module.css";

/** 12 / 8 / 4 visible column guides (desktop / tablet / mobile). */
export default function GuideLines() {
  return (
    <div className={styles.guides} aria-hidden="true">
      {Array.from({ length: 12 }, (_, i) => <span key={i} />)}
    </div>
  );
}
