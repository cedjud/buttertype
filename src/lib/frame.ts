"use client";

import { useEffect, useRef, type RefObject } from "react";

/* One requestAnimationFrame loop for the whole page. Jobs only run while their element is near the viewport. */

type Job = () => void;
const jobs = new Set<Job>();
let raf = 0;

function tick() {
  jobs.forEach((job) => job());
  raf = jobs.size ? requestAnimationFrame(tick) : 0;
}

function addJob(job: Job) {
  jobs.add(job);
  if (!raf) raf = requestAnimationFrame(tick);
  return () => { jobs.delete(job); };
}

/** Run `job` every frame while `ref` is within `margin` of the viewport (`always` skips the gating). */
export function useFrame(ref: RefObject<Element | null> | null, job: Job, { margin = "20% 0px", always = false } = {}) {
  const jobRef = useRef(job);
  useEffect(() => { jobRef.current = job; });

  useEffect(() => {
    const run = () => jobRef.current();
    if (always || !ref) return addJob(run);
    const el = ref.current;
    if (!el) return;
    let remove: (() => void) | null = null;
    const io = new IntersectionObserver(([e]) => {
      if (e.isIntersecting && !remove) { remove = addJob(run); run(); }
      else if (!e.isIntersecting && remove) { remove(); remove = null; }
    }, { rootMargin: margin });
    io.observe(el);
    return () => { io.disconnect(); remove?.(); };
  }, [ref, margin, always]);
}
