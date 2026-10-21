import Nav from "@/components/Nav";
import Axes from "@/components/sections/Axes";
import Features from "@/components/sections/Features";
import Glyphs from "@/components/sections/Glyphs";
import Hero from "@/components/sections/Hero";
import MeltStages from "@/components/sections/MeltStages";
import Norge from "@/components/sections/Norge";
import Tester from "@/components/sections/Tester";

export default function Home() {
  return (
    <>
      <Nav />
      <main>
        <Hero />
        <MeltStages />
        <Axes />
        <Norge />
        <Features />
        <Glyphs />
        <Tester />
      </main>
    </>
  );
}
