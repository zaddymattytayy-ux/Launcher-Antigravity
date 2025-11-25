import React from 'react';

interface StatWidgetProps {
    icon: React.ReactNode;
    label: string;
    value: string | number;
    color?: string;
}

const StatWidget: React.FC<StatWidgetProps> = ({ icon, label, value, color = 'blue' }) => {
    return (
        <div className="rounded-2xl bg-white/10 backdrop-blur border border-white/20 shadow-xl p-6 hover:bg-white/15 transition-all">
            <div className="flex items-center gap-4">
                <div className={`w-14 h-14 rounded-xl bg-${color}-500/20 flex items-center justify-center`}>
                    {icon}
                </div>
                <div>
                    <p className="text-gray-400 text-sm">{label}</p>
                    <p className="text-3xl font-bold text-white">{value}</p>
                </div>
            </div>
        </div>
    );
};

export default StatWidget;
