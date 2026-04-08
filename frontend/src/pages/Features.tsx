import React from 'react';
import { ArrowLeft, Shield, MousePointer2 } from 'lucide-react';
import AntiGravityCanvas from '../components/ui/particle-effect-for-hero';
import { Features } from '../components/ui/features-4';

interface FeaturesProps {
  onBack: () => void;
}

const Navigation: React.FC<{ onBack: () => void }> = ({ onBack }) => {
  return (
    <nav className="absolute top-0 left-0 w-full z-20 flex justify-between items-center p-6 md:p-8">
      <button
        onClick={onBack}
        className="flex items-center gap-2 text-white/70 hover:text-white transition-colors"
      >
        <ArrowLeft size={20} />
        <span className="font-medium">Back</span>
      </button>
      <div className="flex items-center space-x-2">
        <div className="w-8 h-8 bg-gradient-to-br from-brand-500/30 to-brand-400/20 border border-brand-500/40 rounded-full flex items-center justify-center shadow-lg">
          <Shield className="w-5 h-5 text-brand-300" />
        </div>
        <span className="text-white font-medium tracking-wide text-lg">PPE Safety</span>
      </div>
      <div className="w-24" /> {/* Spacer for centering */}
    </nav>
  );
};

export default function FeaturesPage({ onBack }: FeaturesProps) {
  return (
    <div className="relative w-full min-h-screen bg-black overflow-hidden selection:bg-brand-500 selection:text-white">
      <AntiGravityCanvas />
      <Navigation onBack={onBack} />
      <div className="relative z-10 pt-32 pb-20">
        <Features />
      </div>
      
      {/* Scroll Indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-white/30 animate-pulse pointer-events-none z-20">
        <span className="text-[10px] uppercase tracking-[0.2em]">Interact</span>
        <MousePointer2 size={16} />
      </div>
    </div>
  );
}

