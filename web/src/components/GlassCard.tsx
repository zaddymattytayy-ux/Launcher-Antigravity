import React from 'react';

interface GlassCardProps {
    children: React.ReactNode;
    className?: string;
}

const GlassCard: React.FC<GlassCardProps> = ({ children, className = '' }) => {
    return (
        <div className={`rounded-2xl bg-white/10 backdrop-blur border border-white/20 shadow-xl p-6 ${className}`}>
            {children}
        </div>
    );
};

export default GlassCard;
