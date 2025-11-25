import React from 'react';
import { Settings } from 'lucide-react';
import { bridge } from '../services/bridge';
import './TopBar.css';

const TopBar: React.FC = () => {
    const handleLaunch = async () => {
        await bridge.launchGame("1920x1080", true);
    };

    return (
        <header className="topbar">
            {/* Left: Status */}
            <div className="topbar-status">
                Launcher ready
            </div>

            {/* Center: Title */}
            <div className="topbar-title">
                <h1>MU Online Launcher</h1>
                <span className="topbar-subtitle">Season 18 • Experience the Legend</span>
            </div>

            {/* Right: Actions */}
            <div className="topbar-actions">
                <button className="topbar-button settings-button" title="Settings">
                    <Settings size={20} />
                </button>

                <button className="topbar-button start-button" onClick={handleLaunch}>
                    <span>START GAME</span>
                </button>
            </div>
        </header>
    );
};

export default TopBar;
