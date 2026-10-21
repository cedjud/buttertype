import SectionHead from "@/components/SectionHead";
import styles from "./Licence.module.css";

/* No prices, terms or checkout yet — CTAs point at the footer contact placeholder until the client decides. */
const TIERS = [
  { name: "Trial", text: "Try BT Smör in your own layouts before you commit.", cta: "Request trial" },
  { name: "Desktop", text: "Print, packaging, signage, video and everything else you design on a computer.", cta: "Ask for pricing", featured: true },
  { name: "Web", text: "Self-hosted WOFF2 for websites, with the variable axes and features intact.", cta: "Ask for pricing" },
  { name: "Custom", text: "More glyphs, more languages, a brand-specific melt. Let’s make your version.", cta: "Get in touch" },
];

export default function Licence() {
  return (
    <section id="licence" className={styles.licence} aria-labelledby="licence-title">
      <SectionHead
        id="licence-title"
        label="10 — Get the fonts"
        title={<>Pick<span className="br-m" /> your pat.</>}
        titleClassName={styles.title}
      >
        <p>Choose the licence that fits. Every plan includes the variable font and both stylistic sets.</p>
      </SectionHead>

      <ul className={styles.tiers}>
        {TIERS.map((t) => (
          <li key={t.name} className={`${styles.tier} ${t.featured ? styles.featured : ""}`}>
            <div className={styles.tierBody}>
              <h3 className={`${styles.name} bt bt-hover`}>{t.name}</h3>
              <p className={styles.text}>{t.text}</p>
            </div>
            <a href="#contact" className={styles.cta} aria-label={`${t.cta}: ${t.name} licence`}>
              <span>{t.cta}</span><span aria-hidden="true">→</span>
            </a>
          </li>
        ))}
      </ul>
    </section>
  );
}
