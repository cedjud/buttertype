import type { Metadata, Viewport } from "next";
import { DM_Mono, Familjen_Grotesk } from "next/font/google";
import { preload } from "react-dom";
import "./globals.css";

const familjen = Familjen_Grotesk({
  variable: "--font-familjen",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

const dmMono = DM_Mono({
  variable: "--font-dm-mono",
  subsets: ["latin"],
  weight: ["400", "500"],
});

export const metadata: Metadata = {
  title: "BT Smör — a variable typeface made for Norway",
  description:
    "BT Smör is a butter-inspired variable typeface. Razor-sharp when cold, gooey when warm. Three axes: MELT, BUBL and SLMP.",
};

export const viewport: Viewport = {
  themeColor: "#FFD21F",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  // The display face is declared in tokens.css (family "BT Smör"); preload it so the hero never waits.
  preload("/fonts/BTSmor.woff2", { as: "font", type: "font/woff2", crossOrigin: "anonymous" });

  return (
    <html lang="en" className={`${familjen.variable} ${dmMono.variable}`}>
      <body>{children}</body>
    </html>
  );
}
