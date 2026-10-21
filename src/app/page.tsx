import Nav from "@/components/Nav";
import Hero from "@/components/sections/Hero";
import MeltStages from "@/components/sections/MeltStages";

export default function Home() {
  return (
    <>
      <Nav />
      <main>
        <Hero />
        <MeltStages />
      </main>
    </>
  );
}
