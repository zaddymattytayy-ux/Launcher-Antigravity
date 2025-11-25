import React from 'react';
import {
    HiHome,
    HiChartBar,
    HiCurrencyDollar,
    HiBookOpen,
    HiCalendarDays,
    HiShieldCheck,
    HiShieldExclamation,
    HiPower
} from 'react-icons/hi2';
import { bridge } from '../services/bridge';
import './Sidebar.css';

type TabKey = 'home' | 'rankings' | 'donate' | 'guides' | 'events';

interface SidebarProps {
    activeTab: TabKey;
    onTabChange: (tab: TabKey) => void;
    isGameInstalled: boolean;
    onExitClick: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange, isGameInstalled, onExitClick }) => {
    const navItems = [
        { id: 'home' as const, icon: HiHome, label: 'Home' },
        { id: 'rankings' as const, icon: HiChartBar, label: 'Rankings' },
        { id: 'donate' as const, icon: HiCurrencyDollar, label: 'Donate' },
        { id: 'guides' as const, icon: HiBookOpen, label: 'Guides' },
        { id: 'events' as const, icon: HiCalendarDays, label: 'Events' },
    ];


    const handleMouseDown = () => {
        console.log('[SIDEBAR] Mouse down on sidebar - calling bridge.startDrag()');
        bridge.startDrag();
    };


    return (
        <aside className="sidebar react-sidebar" onMouseDown={handleMouseDown}>
            <div className="sidebar-top">
                <button
                    className="logo-button"
                    onClick={() => onTabChange('home')}
                    title="Opal MU - Home"
                >
                    <span className="logo-text">OM</span>
                </button>
            </div>

            <div className="sidebar-middle">
                <div className="nav-icons">
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = activeTab === item.id;

                        return (
                            <button
                                key={item.id}
                                className={`sidebar-icon nav-icon ${isActive ? 'active' : ''}`}
                                onClick={() => onTabChange(item.id)}
                                title={item.label}
                            >
                                <Icon size={20} />
                            </button>
                        );
                    })}
                </div>
            </div>

            <div className="sidebar-bottom">
                <div
                    className={`sidebar-icon status-icon ${isGameInstalled ? 'installed' : 'not-installed'}`}
                    title={isGameInstalled ? 'Game installation detected' : 'Game not installed'}
                >
                    {isGameInstalled ? <HiShieldCheck size={20} /> : <HiShieldExclamation size={20} />}
                </div>

                <button
                    className="sidebar-icon exit-button"
                    onClick={onExitClick}
                    title="Exit"
                >
                    <HiPower size={20} />
                </button>
            </div>
        </aside>
    );
};

export default Sidebar;
