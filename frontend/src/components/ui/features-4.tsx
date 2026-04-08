import { Cpu, Fingerprint, Pencil, Settings2, Sparkles, Zap, Shield, Eye, AlertTriangle, BarChart3, Brain, Database } from 'lucide-react';

interface FeaturesProps {
  className?: string;
}

export function Features({ className = '' }: FeaturesProps) {
  const features = [
    {
      icon: Zap,
      title: 'Real-Time Detection',
      description: 'Instant AI-powered detection of helmets and safety vests with high accuracy and low latency.',
    },
    {
      icon: Cpu,
      title: 'Powerful Processing',
      description: 'YOLOv8 and ByteTrack integration for robust person tracking and PPE association.',
    },
    {
      icon: Shield,
      title: 'Safety First',
      description: 'Comprehensive compliance monitoring to protect workers and meet regulatory requirements.',
    },
    {
      icon: Eye,
      title: 'Adaptive Monitoring',
      description: 'Scene-aware quality analysis that adapts to lighting and environmental conditions.',
    },
    {
      icon: Settings2,
      title: 'Full Control',
      description: 'Configurable thresholds, alerts, and logging to match your safety protocols.',
    },
    {
      icon: Brain,
      title: 'AI-Enhanced',
      description: 'Temporal smoothing and PPE memory system for stable, accurate tracking.',
    },
  ];

  return (
    <section className={`py-12 md:py-20 ${className}`}>
      <div className="mx-auto max-w-5xl space-y-8 px-6 md:space-y-16">
        <div className="relative z-10 mx-auto max-w-xl space-y-6 text-center md:space-y-12">
          <h2 className="text-balance text-4xl font-medium text-white lg:text-5xl">
            The foundation for workplace safety monitoring
          </h2>
          <p className="text-white/70 text-lg">
            Tibyan is evolving to be more than just detection. It supports an entire ecosystem 
            of APIs and platforms helping safety teams and businesses innovate.
          </p>
        </div>
        <div className="relative mx-auto grid max-w-2xl lg:max-w-4xl divide-x divide-y divide-white/10 border border-white/20 *:p-12 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div key={index} className="space-y-3">
                <div className="flex items-center gap-2">
                  <Icon className="size-4 text-brand-400" />
                  <h3 className="text-sm font-medium text-white">{feature.title}</h3>
                </div>
                <p className="text-sm text-white/60">{feature.description}</p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}


