import React from 'react';
import { MousePointer2, Info, ArrowRight, Shield } from 'lucide-react';
import AntiGravityCanvas from '../components/ui/particle-effect-for-hero';

interface WelcomeProps {
  onGetStarted: () => void;
  setPage: (page: string) => void;
}

const Navigation: React.FC<{ onGetStarted: () => void; setPage: (page: string) => void }> = ({ onGetStarted, setPage }) => {
  return (
    <nav className="absolute top-0 left-0 w-full z-20 flex justify-between items-center p-6 md:p-8">
      <div className="flex items-center space-x-2">
        <div className="w-8 h-8 bg-gradient-to-br from-brand-500/30 to-brand-400/20 border border-brand-500/40 rounded-full flex items-center justify-center shadow-lg">
          <Shield className="w-5 h-5 text-brand-300" />
        </div>
        <span className="text-white font-medium tracking-wide text-lg">PPE Safety</span>
      </div>
      <div className="hidden md:flex space-x-8 text-sm font-medium text-white/70">
        <button onClick={onGetStarted} className="hover:text-white transition-colors">
          Dashboard
        </button>
        <button onClick={() => setPage("features")} className="hover:text-white transition-colors">
          Features
        </button>
        <button onClick={() => setPage("about")} className="hover:text-white transition-colors">
          About
        </button>
      </div>
      <button 
        onClick={() => setPage("info")}
        className="text-white/80 hover:text-white transition-colors"
      >
        <Info size={24} />
      </button>
    </nav>
  );
};

const HeroContent: React.FC<{ onGetStarted: () => void }> = ({ onGetStarted }) => {
  return (
    <div className="absolute inset-0 z-10 flex flex-col items-center justify-center pointer-events-none px-4">
      <div className="max-w-4xl w-full text-center space-y-8">
        <div className="inline-block animate-fade-in-up">
          <span className="py-1 px-3 border border-white/20 rounded-full text-xs font-mono text-white/60 tracking-widest uppercase bg-white/5 backdrop-blur-sm">
            AI-Enhanced Safety Monitoring
          </span>
        </div>
        
        <h1 className="text-6xl md:text-8xl lg:text-9xl font-bold text-transparent bg-clip-text bg-gradient-to-b from-white to-white/40 tracking-tighter mix-blend-difference">
          PPE<br/>Monitoring
        </h1>
        
        <p className="max-w-2xl mx-auto text-lg md:text-xl text-white/60 font-light leading-relaxed">
          Real-time AI-powered detection and compliance monitoring for Personal Protective Equipment. 
          Keep your workplace safe with intelligent tracking and instant alerts.
        </p>

        <div className="pt-8 pointer-events-auto">
          <button 
            onClick={onGetStarted}
            className="group relative inline-flex items-center gap-3 px-8 py-4 bg-white text-black rounded-full font-bold tracking-wide overflow-hidden transition-transform hover:scale-105 active:scale-95"
          >
            <span className="relative z-10">Start Monitoring</span>
            <ArrowRight className="w-4 h-4 relative z-10 group-hover:translate-x-1 transition-transform" />
            <div className="absolute inset-0 bg-brand-500 transform scale-x-0 group-hover:scale-x-100 transition-transform origin-left duration-300 ease-out opacity-10"></div>
          </button>
        </div>

        <div className="flex flex-wrap justify-center gap-4 text-xs sm:text-sm text-white/50 pt-4">
          <span className="px-3 py-1 rounded-full bg-black/30 border border-white/10">
            ⚡ Real-time Detection
          </span>
          <span className="px-3 py-1 rounded-full bg-black/30 border border-white/10">
            📡 WebSocket Streaming
          </span>
          <span className="px-3 py-1 rounded-full bg-black/30 border border-white/10">
            📊 Compliance Analytics
          </span>
        </div>
      </div>
    </div>
  );
};

export default function Welcome({ onGetStarted, setPage }: WelcomeProps) {
  return (
    <div className="relative w-full h-screen bg-black overflow-hidden selection:bg-brand-500 selection:text-white">
      <AntiGravityCanvas />
      <Navigation onGetStarted={onGetStarted} setPage={setPage} />
      <HeroContent onGetStarted={onGetStarted} />
      
      {/* Scroll Indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-white/30 animate-pulse pointer-events-none">
        <span className="text-[10px] uppercase tracking-[0.2em]">Interact</span>
        <MousePointer2 size={16} />
      </div>
    </div>
  );
}
