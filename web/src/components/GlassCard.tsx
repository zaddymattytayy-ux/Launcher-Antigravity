import React from 'react';

interface GlassCardProps {
    children: React.ReactNode;
    className?: string;
}

const GlassCard: React.FC<GlassCardProps> = ({ children, className = '' }) => {
    return (
        <div
            className={className}
            style={{
                position: 'relative',
                borderRadius: '16px',
                background: 'rgba(255, 255, 255, 0.08)',
                border: '1px solid rgba(255, 255, 255, 0.22)',
                backdropFilter: 'none',
                WebkitBackdropFilter: 'none',
                boxShadow: '0 0 40px rgba(0, 0, 0, 0.25)',
                padding: '24px'
            }}
        >
            {children}
        </div>
    );
};

export default GlassCard;
