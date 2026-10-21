import type { ReactNode } from "react";
import styles from "./SectionHead.module.css";

type Props = {
  id: string;
  label: string;
  title: ReactNode;
  titleClassName?: string;
  children?: ReactNode;
};

/** Section header: label + display title over 8 columns, intro over 4. Stacks below 1024. Rule colour = currentColor of `--rule`. */
export default function SectionHead({ id, label, title, titleClassName, children }: Props) {
  return (
    <div className={styles.head}>
      <div className={styles.main}>
        <p className={styles.label}>{label}</p>
        <h2 id={id} className={`${styles.title} bt ${titleClassName ?? ""}`}>{title}</h2>
      </div>
      <div className={styles.aside}>{children}</div>
    </div>
  );
}
