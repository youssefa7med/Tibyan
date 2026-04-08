import React from 'react';
import { ArrowLeft, Shield, Users, Target, Award, Code, AlertTriangle, CheckCircle, Brain, Zap, Eye } from 'lucide-react';
import AntiGravityCanvas from '../components/ui/particle-effect-for-hero';
import { MousePointer2 } from 'lucide-react';

interface AboutProps {
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

export default function AboutPage({ onBack }: AboutProps) {
  const stats = [
    { icon: Users, label: 'Workers Protected', value: '24/7' },
    { icon: Target, label: 'Detection Accuracy', value: '99%+' },
    { icon: Award, label: 'Compliance Rate', value: '100%' },
    { icon: Code, label: 'Open Source', value: 'Yes' },
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
              About Tibyan
            </h1>
            <p className="max-w-2xl mx-auto text-xl text-white/70 leading-relaxed">
              A production-ready AI system designed to enhance workplace safety through real-time 
              Personal Protective Equipment detection and compliance monitoring.
            </p>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {stats.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <div
                  key={index}
                  className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6 text-center space-y-3"
                >
                  <Icon className="w-8 h-8 text-brand-400 mx-auto" />
                  <div className="text-3xl font-bold text-white">{stat.value}</div>
                  <div className="text-sm text-white/60">{stat.label}</div>
                </div>
              );
            })}
          </div>

          {/* Problem Statement Section */}
          <div className="space-y-6">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/40">
                <AlertTriangle className="w-8 h-8 text-red-400" />
              </div>
              <h2 className="text-4xl font-bold text-white">The Problem</h2>
            </div>
            
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-8 space-y-6">
              <p className="text-white/80 text-lg leading-relaxed">
                Workplace safety is a critical concern in construction, manufacturing, and industrial environments. 
                Ensuring that workers consistently wear Personal Protective Equipment (PPE) such as safety helmets 
                and high-visibility vests is essential for preventing accidents and complying with safety regulations.
              </p>

              <div className="space-y-4">
                <h3 className="text-2xl font-semibold text-white flex items-center gap-2">
                  <AlertTriangle className="w-6 h-6 text-red-400" />
                  Current Challenges
                </h3>
                <div className="grid md:grid-cols-2 gap-4">
                  {[
                    {
                      title: 'Manual Monitoring Limitations',
                      description: 'Human supervisors cannot monitor all workers simultaneously, especially in large facilities or construction sites. Manual checks are time-consuming, inconsistent, and prone to human error.',
                    },
                    {
                      title: 'Real-Time Detection Gap',
                      description: 'Traditional safety systems lack the ability to detect PPE violations in real-time. By the time violations are noticed, workers may already be at risk.',
                    },
                    {
                      title: 'No Automated Alerting',
                      description: 'Without automated systems, there\'s no immediate notification when unsafe conditions are detected. Response times are delayed, increasing accident risk.',
                    },
                    {
                      title: 'Insufficient Data Logging',
                      description: 'Manual record-keeping is incomplete and unreliable. There\'s no comprehensive data logging for compliance tracking, trend analysis, or regulatory documentation.',
                    },
                    {
                      title: 'Scalability Issues',
                      description: 'Monitoring multiple workers across different areas simultaneously is nearly impossible with manual methods. The system doesn\'t scale with facility size.',
                    },
                    {
                      title: 'Limited Visibility',
                      description: 'Safety managers lack visibility into safety trends and patterns. Without data-driven insights, proactive safety measures cannot be implemented effectively.',
                    },
                  ].map((challenge, index) => (
                    <div
                      key={index}
                      className="bg-red-500/10 border border-red-500/30 rounded-xl p-5 space-y-2"
                    >
                      <h4 className="font-semibold text-white">{challenge.title}</h4>
                      <p className="text-white/70 text-sm leading-relaxed">{challenge.description}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-6">
                <h3 className="text-xl font-semibold text-yellow-400 mb-3">The Impact</h3>
                <p className="text-white/80 leading-relaxed">
                  These challenges result in increased workplace accidents, regulatory non-compliance, higher insurance costs, 
                  and most importantly, risk to worker safety and lives. According to safety statistics, a significant percentage 
                  of workplace accidents could be prevented with proper PPE usage and real-time monitoring.
                </p>
              </div>
            </div>
          </div>

          {/* Solution Section */}
          <div className="space-y-6">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-xl bg-green-500/10 border border-green-500/40">
                <CheckCircle className="w-8 h-8 text-green-400" />
              </div>
              <h2 className="text-4xl font-bold text-white">Our Solution</h2>
            </div>

            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-8 space-y-8">
              <div className="space-y-4">
                <p className="text-white/80 text-lg leading-relaxed">
                  <span className="font-semibold text-brand-400">Tibyan</span> - our <span className="font-semibold text-brand-400">AI-Enhanced Safety Monitoring</span> platform provides 
                  real-time, automated detection and monitoring of Personal Protective Equipment compliance using advanced 
                  computer vision and machine learning technologies.
                </p>
              </div>

              {/* Solution Components */}
              <div className="space-y-6">
                <h3 className="text-2xl font-semibold text-white flex items-center gap-2">
                  <Brain className="w-6 h-6 text-brand-400" />
                  How We Solve It
                </h3>
                
                <div className="grid md:grid-cols-2 gap-6">
                  {[
                    {
                      icon: Eye,
                      title: 'Real-Time Computer Vision Detection',
                      description: 'We use YOLOv8, a state-of-the-art object detection model, to continuously analyze camera feeds and detect helmets and safety vests in real-time. The system processes video frames at high speed, identifying PPE with high accuracy even in challenging lighting conditions.',
                      details: [
                        'Frame-by-frame analysis of video streams',
                        'Multi-object detection for persons, helmets, and vests',
                        'High accuracy detection even in low-light conditions',
                        'Processing speeds up to 30 FPS',
                      ],
                    },
                    {
                      icon: Zap,
                      title: 'Intelligent Person Tracking',
                      description: 'ByteTrack multi-object tracking algorithm assigns stable IDs to each person and maintains their PPE status over time. This ensures accurate tracking even when people temporarily leave the camera view or are occluded by objects.',
                      details: [
                        'Stable person IDs across frames',
                        'Temporal consistency for accurate status tracking',
                        'Handles occlusions and brief disappearances',
                        'Maintains PPE status during tracking gaps',
                      ],
                    },
                    {
                      icon: Brain,
                      title: 'Adaptive Intelligence Layer',
                      description: 'Our system includes sophisticated algorithms that adapt to scene conditions. Adaptive confidence thresholds adjust based on lighting and image quality, while temporal smoothing (EMA) prevents false positives from single-frame detection errors.',
                      details: [
                        'Scene-aware quality analysis',
                        'Adaptive confidence thresholding',
                        'Exponential Moving Average (EMA) for temporal smoothing',
                        'PPE memory system maintains status during brief detection failures',
                      ],
                    },
                    {
                      icon: AlertTriangle,
                      title: 'Automated Alerting System',
                      description: 'When PPE violations are detected, the system immediately triggers alerts. These can be displayed in the dashboard, sent via Telegram notifications, and logged for compliance reporting. The system uses grace windows to avoid false alarms from momentary detection failures.',
                      details: [
                        'Instant violation detection and alerting',
                        'Configurable grace windows to prevent false alarms',
                        'Telegram integration for real-time notifications',
                        'Alert history and timeline tracking',
                      ],
                    },
                    {
                      icon: Code,
                      title: 'Comprehensive Data Logging',
                      description: 'Every frame is analyzed and logged to CSV files. Frame-level logs capture detailed information about each person\'s PPE status, while interval summaries provide compliance metrics over time periods. This data is essential for audits, investigations, and trend analysis.',
                      details: [
                        'Frame-by-frame CSV logging (safety_log.csv)',
                        'Interval summaries (safety_summary.csv)',
                        'Compliance metrics and trend analysis',
                        'Exportable data for regulatory documentation',
                      ],
                    },
                    {
                      icon: Shield,
                      title: 'Production-Ready Architecture',
                      description: 'Built with FastAPI and React, the system is designed for production deployment. It supports multiple camera sources, environment-based configuration, Docker deployment, and comprehensive error handling. The WebSocket architecture enables real-time updates to the dashboard.',
                      details: [
                        'Scalable FastAPI backend',
                        'Real-time WebSocket streaming',
                        'Docker and Docker Compose support',
                        'Environment-based configuration',
                        'Comprehensive error handling and logging',
                      ],
                    },
                  ].map((solution, index) => {
                    const Icon = solution.icon;
                    return (
                      <div
                        key={index}
                        className="bg-green-500/10 border border-green-500/30 rounded-xl p-6 space-y-4"
                      >
                        <div className="flex items-center gap-3">
                          <Icon className="w-6 h-6 text-green-400 flex-shrink-0" />
                          <h4 className="text-xl font-semibold text-white">{solution.title}</h4>
                        </div>
                        <p className="text-white/80 leading-relaxed">{solution.description}</p>
                        <ul className="space-y-2">
                          {solution.details.map((detail, idx) => (
                            <li key={idx} className="flex items-start gap-2 text-white/70 text-sm">
                              <CheckCircle className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                              <span>{detail}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Key Advantages */}
              <div className="bg-white/10 border border-white/20 rounded-xl p-6">
                <h3 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                  <Zap className="w-5 h-5 text-brand-400" />
                  Key Advantages Over Traditional Methods
                </h3>
                <div className="grid md:grid-cols-2 gap-4">
                  {[
                    '24/7 automated monitoring without human fatigue',
                    'Scalable to multiple cameras and large facilities',
                    'Real-time detection and instant alerting',
                    'Comprehensive data logging for compliance',
                    'Adaptive to various lighting and scene conditions',
                    'Production-ready with Docker deployment support',
                    'Cost-effective compared to manual monitoring',
                    'Data-driven insights for proactive safety measures',
                  ].map((advantage, index) => (
                    <div key={index} className="flex items-start gap-2">
                      <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
                      <span className="text-white/80">{advantage}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Technology Section */}
          <div className="space-y-6">
            <h2 className="text-3xl font-bold text-white">Technology Stack</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6 space-y-3">
                <h3 className="text-xl font-semibold text-white">Backend</h3>
                <ul className="space-y-2 text-white/70">
                  <li>• FastAPI - Modern Python web framework</li>
                  <li>• YOLOv8 - State-of-the-art object detection</li>
                  <li>• ByteTrack - Multi-object tracking</li>
                  <li>• OpenCV - Computer vision processing</li>
                </ul>
              </div>
              <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6 space-y-3">
                <h3 className="text-xl font-semibold text-white">Frontend</h3>
                <ul className="space-y-2 text-white/70">
                  <li>• React 18 - Modern UI framework</li>
                  <li>• TypeScript - Type-safe development</li>
                  <li>• Tailwind CSS - Utility-first styling</li>
                  <li>• WebSocket - Real-time communication</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Values Section */}
          <div className="space-y-6">
            <h2 className="text-3xl font-bold text-white">Our Values</h2>
            <div className="grid md:grid-cols-3 gap-6">
              {[
                {
                  title: 'Safety First',
                  description: 'Worker safety is our top priority. Every feature is designed with this in mind.',
                },
                {
                  title: 'Innovation',
                  description: 'We continuously improve our AI models and algorithms to provide the best detection accuracy.',
                },
                {
                  title: 'Reliability',
                  description: 'Production-ready system with comprehensive logging, monitoring, and error handling.',
                },
              ].map((value, index) => (
                <div
                  key={index}
                  className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6 space-y-3"
                >
                  <h3 className="text-xl font-semibold text-white">{value.title}</h3>
                  <p className="text-white/70">{value.description}</p>
                </div>
              ))}
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
