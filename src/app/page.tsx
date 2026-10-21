import Footer from "@/components/Footer";
import Nav from "@/components/Nav";
import Axes from "@/components/sections/Axes";
import Features from "@/components/sections/Features";
import Glyphs from "@/components/sections/Glyphs";
import Hero from "@/components/sections/Hero";
import InUse from "@/components/sections/InUse";
import Licence from "@/components/sections/Licence";
import MeltStages from "@/components/sections/MeltStages";
import Norge from "@/components/sections/Norge";
import Specs from "@/components/sections/Specs";
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
        <InUse />
        <Specs />
        <Licence />
      </main>
      <Footer />
    </>
  );
}
