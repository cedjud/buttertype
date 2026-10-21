/* BT Smör character set (108 glyphs incl. alternates; these are the 90 encoded ones). */

export const GLYPH_GROUPS: { name: string; chars: string[] }[] = [
  { name: "Nordic", chars: Array.from("ÆØÅæøåÄÖÉäöé") },
  { name: "Uppercase", chars: Array.from("ABCDEFGHIJKLMNOPQRSTUVWXYZ") },
  { name: "Lowercase", chars: Array.from("abcdefghijklmnopqrstuvwxyz") },
  { name: "Figures", chars: Array.from("0123456789") },
  { name: "Punctuation", chars: Array.from(".,:;!?-–—'\"()/+=") },
];

const NAMES: Record<string, string> = {
  ".": "Full Stop", ",": "Comma", ":": "Colon", ";": "Semicolon", "!": "Exclamation Mark", "?": "Question Mark",
  "-": "Hyphen-Minus", "–": "En Dash", "—": "Em Dash", "'": "Apostrophe", "\"": "Quotation Mark",
  "(": "Left Parenthesis", ")": "Right Parenthesis", "/": "Solidus", "+": "Plus Sign", "=": "Equals Sign",
  "Æ": "Latin Capital Letter AE", "æ": "Latin Small Letter AE",
  "Ø": "Latin Capital Letter O with Stroke", "ø": "Latin Small Letter O with Stroke",
  "Å": "Latin Capital Letter A with Ring Above", "å": "Latin Small Letter A with Ring Above",
  "Ä": "Latin Capital Letter A with Diaeresis", "ä": "Latin Small Letter A with Diaeresis",
  "Ö": "Latin Capital Letter O with Diaeresis", "ö": "Latin Small Letter O with Diaeresis",
  "É": "Latin Capital Letter E with Acute", "é": "Latin Small Letter E with Acute",
};
const DIGITS = ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"];

export function glyphName(c: string) {
  if (NAMES[c]) return NAMES[c];
  if (/[A-Z]/.test(c)) return `Latin Capital Letter ${c}`;
  if (/[a-z]/.test(c)) return `Latin Small Letter ${c.toUpperCase()}`;
  if (/[0-9]/.test(c)) return `Digit ${DIGITS[+c]}`;
  return c;
}

export const codePoint = (c: string) => "U+" + c.codePointAt(0)!.toString(16).toUpperCase().padStart(4, "0");

/** ss01: double-storey a. ss02: square dots. */
export const hasSs01 = (c: string) => "aåä".includes(c);
export const hasSs02 = (c: string) => "ijäöÄÖ.,:;!?".includes(c);
