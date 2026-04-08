import React from 'react';
import { ArrowLeft, Shield, BookOpen, Code, FileText, Github, ExternalLink, MousePointer2 } from 'lucide-react';
import AntiGravityCanvas from '../components/ui/particle-effect-for-hero';

interface InfoProps {
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

export default function InfoPage({ onBack }: InfoProps) {
  const quickLinks = [
    {
      icon: BookOpen,
      title: 'Documentation',
      description: 'Comprehensive guides and API references',
      href: '#',
    },
    {
      icon: Code,
      title: 'API Reference',
      description: 'REST API and WebSocket documentation',
      href: '#',
    },
    {
      icon: FileText,
      title: 'Deployment Guide',
      description: 'Step-by-step deployment instructions',
      href: '#',
    },
    {
      icon: Github,
      title: 'GitHub Repository',
      description: 'View source code and contribute',
      href: '#',
    },
  ];

  const systemInfo = [
    { label: 'Version', value: '1.0.0' },
    { label: 'License', value: 'MIT' },
    { label: 'Framework', value: 'React + FastAPI' },
    { label: 'AI Model', value: 'YOLOv8' },
  ];

  return (
    <div className="relative w-full min-h-screen bg-black overflow-hidden selection:bg-brand-500 selection:text-white">
      <AntiGravityCanvas />
      <Navigation onBack={onBack} />
      <div className="relative z-10 pt-32 pb-20">
        <div className="mx-auto max-w-5xl space-y-16 px-6">
          {/* Hero Section */}
          <div className="text-center space-y-6">
            <h1 className="text-5xl md:text-7xl font-bold text-transparent bg-clip-text bg-gradient-to-b from-white to-white/40">
              Information & Resources
            </h1>
            <p className="max-w-2xl mx-auto text-xl text-white/70 leading-relaxed">
              Everything you need to understand, deploy, and extend the PPE Safety Monitoring system.
            </p>
          </div>

          {/* Quick Links */}
          <div className="space-y-6">
            <h2 className="text-3xl font-bold text-white">Quick Links</h2>
            <div className="grid md:grid-cols-2 gap-6">
              {quickLinks.map((link, index) => {
                const Icon = link.icon;
                return (
                  <a
                    key={index}
                    href={link.href}
                    className="group bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6 space-y-3 hover:bg-white/10 transition-all"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Icon className="w-6 h-6 text-brand-400" />
                        <h3 className="text-xl font-semibold text-white">{link.title}</h3>
                      </div>
                      <ExternalLink className="w-5 h-5 text-white/40 group-hover:text-white transition-colors" />
                    </div>
                    <p className="text-white/70">{link.description}</p>
                  </a>
                );
              })}
            </div>
          </div>

          {/* System Information */}
          <div className="space-y-6">
            <h2 className="text-3xl font-bold text-white">System Information</h2>
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-8">
              <div className="grid md:grid-cols-2 gap-6">
                {systemInfo.map((info, index) => (
                  <div key={index} className="flex justify-between items-center border-b border-white/10 pb-4">
                    <span className="text-white/70">{info.label}</span>
                    <span className="text-white font-semibold">{info.value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Getting Started */}
          <div className="space-y-6">
            <h2 className="text-3xl font-bold text-white">Getting Started</h2>
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-8 space-y-6">
              <div className="space-y-4">
                <h3 className="text-xl font-semibold text-white">Quick Start</h3>
                <ol className="space-y-3 text-white/70 list-decimal list-inside">
                  <li>Start the FastAPI backend: <code className="bg-black/30 px-2 py-1 rounded text-brand-400">python -m backend.app.main</code></li>
                  <li>Start the frontend: <code className="bg-black/30 px-2 py-1 rounded text-brand-400">cd frontend && npm run dev</code></li>
                  <li>Navigate to the Dashboard and start monitoring</li>
                </ol>
              </div>
              <div className="space-y-4">
                <h3 className="text-xl font-semibold text-white">Configuration</h3>
                <p className="text-white/70">
                  Configure camera sources, detection thresholds, and alert settings in the Settings page. 
                  All configuration is environment-based and can be customized for your deployment.
                </p>
              </div>
            </div>
          </div>

          {/* Support */}
          <div className="space-y-6">
            <h2 className="text-3xl font-bold text-white">Support & Contact</h2>
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-8 space-y-4">
              <p className="text-white/70">
                For questions, issues, or contributions, please refer to the documentation or 
                open an issue on GitHub. We're committed to helping you deploy and maintain 
                a safe workplace monitoring system.
              </p>
            </div>
          </div>
        </div>
      </div>
      
      {/* Scroll Indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-white/30 animate-pulse pointer-events-none z-20">
        <span className="text-[10px] uppercase tracking-[0.2em]">Interact</span>
        <MousePointer2 size={16} />
      </div>
    </div>
  );
}

