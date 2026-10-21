"use client";

import { useSyncExternalStore } from "react";
import { MOODS, type StageName } from "./axes";

/* Site-wide "Mood" (nav selector): a base MELT for the display type. Mirrored to --mood-m on <html>. */

let mood: StageName = "Solid";
const listeners = new Set<() => void>();

export const moodMelt = (name: StageName = mood) => MOODS.find((x) => x.name === name)?.m ?? 0;
export const getMood = () => mood;

export function setMood(name: StageName) {
  mood = name;
  document.documentElement.style.setProperty("--mood-m", String(moodMelt(name)));
  listeners.forEach((l) => l());
}

function subscribe(l: () => void) {
  listeners.add(l);
  return () => { listeners.delete(l); };
}

export const useMood = () => useSyncExternalStore(subscribe, getMood, () => "Solid" as StageName);
