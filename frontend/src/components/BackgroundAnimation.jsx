import React from 'react';
import { Bot, Camera, Eye, Activity, Radio, Cpu, Server, ShieldCheck } from 'lucide-react';
import './BackgroundAnimation.css';

const BackgroundAnimation = () => {
  return (
    <div className="tech-background">
      {/* Animated Grid */}
      <div className="grid-overlay"></div>
      
      {/* Floating Tech Objects */}
      <div className="floating-tech-objects">
        <div className="tech-obj obj-bot">
          <Bot size={60} strokeWidth={1.5} />
          <div className="scan-beam"></div>
        </div>
        
        <div className="tech-obj obj-camera">
          <Camera size={50} strokeWidth={1.5} />
          <div className="record-dot"></div>
        </div>
        
        <div className="tech-obj obj-eye">
          <Eye size={45} strokeWidth={1.5} />
        </div>

        <div className="tech-obj obj-server">
          <Server size={55} strokeWidth={1.5} />
          <div className="data-flow"></div>
        </div>

        <div className="tech-obj obj-shield">
          <ShieldCheck size={40} strokeWidth={1.5} />
        </div>

        {/* Background Particles */}
        <div className="particle p1"><Activity size={20} /></div>
        <div className="particle p2"><Radio size={25} /></div>
        <div className="particle p3"><Cpu size={22} /></div>
      </div>
    </div>
  );
};

export default BackgroundAnimation;
