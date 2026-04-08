"use client";

import { WavyBackground } from "./wavy-background";
import RadialOrbitalTimeline from "./radial-orbital-timeline";
import { RadialOrbitalTimelineDemo } from "./radial-orbital-timeline-demo";

export function WavyBackgroundDemo() {
  return (
    <WavyBackground
      colors={["#38bdf8", "#818cf8", "#c084fc", "#e879f9", "#22d3ee"]}
      waveWidth={50}
      backgroundFill="black"
      blur={10}
      speed="fast"
      waveOpacity={0.5}
    >
      <RadialOrbitalTimelineDemo />
    </WavyBackground>
  );
}

export { WavyBackgroundDemo };


