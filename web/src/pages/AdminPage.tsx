import React from 'react';
import GlassCard from '../components/GlassCard';
import { Users, Server, Settings, Shield } from 'lucide-react';

const AdminPage: React.FC = () => {
    return (
        <div className="p-6 space-y-8">
            <div className="text-center mb-8">
                <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-red-600 mb-3">
                    Admin Control Panel
                </h1>
                <p className="text-gray-300 text-lg">Server management and administration</p>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {[
                    { label: 'Online', value: '1,234', icon: Users, color: 'green' },
                    { label: 'Uptime', value: '99.9%', icon: Server, color: 'blue' },
                    { label: 'DB Size', value: '2.4GB', icon: Settings, color: 'purple' },
                    { label: 'Alerts', value: '0', icon: Shield, color: 'yellow' },
                ].map((stat) => {
                    const Icon = stat.icon;
                    return (
                        <GlassCard key={stat.label} className="p-4">
                            <div className="flex items-center gap-3">
                                <div className={`w-10 h-10 rounded-lg bg-${stat.color}-500/20 flex items-center justify-center`}>
                                    <Icon className={`text-${stat.color}-400`} size={20} />
                                </div>
                                <div>
                                    <p className="text-gray-400 text-xs">{stat.label}</p>
                                    <p className="text-xl font-bold text-white">{stat.value}</p>
                                </div>
                            </div>
                        </GlassCard>
                    );
                })}
            </div>

            {/* Admin Actions */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {[
                    { title: 'Player Management', actions: ['View Online Players', 'Ban/Unban Player', 'Send Global Message'] },
                    { title: 'Server Control', actions: ['Restart Server', 'Maintenance Mode', 'View Server Logs'] },
                    { title: 'Configuration', actions: ['Edit Server Settings', 'Manage Events', 'Drop Rate Settings'] },
                    { title: 'Security', actions: ['View Ban List', 'Anti-Cheat Logs', 'IP Whitelist'] },
                ].map((section) => (
                    <GlassCard key={section.title}>
                        <h3 className="text-xl font-bold text-white mb-4">{section.title}</h3>
                        <div className="space-y-2">
                            {section.actions.map((action) => (
                                <button
                                    key={action}
                                    className="w-full bg-white/5 hover:bg-white/10 border border-white/10 text-white py-2 px-4 rounded-lg text-sm transition-all text-left"
                                >
                                    {action}
                                </button>
                            ))}
                        </div>
                    </GlassCard>
                ))}
            </div>
        </div>
    );
};

export default AdminPage;
