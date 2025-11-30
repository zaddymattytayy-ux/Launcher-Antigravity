import React, { useState } from 'react';
import { HiPlay, HiCog6Tooth, HiArrowDown } from 'react-icons/hi2';
import './HomePage.css';
import BackgroundShell from '../components/layout/BackgroundShell';
import StatusHeader from '../components/layout/StatusHeader';
import { bridge } from '../services/bridge';

interface HomePageProps {
    isAdmin: boolean;
    launcherUpdateState?: 'update_required' | 'downloading';
    downloadProgress?: number;
    onSettingsClick: () => void;
    onStartUpdate?: () => void;
    onlinePlayers: number;
    maxPlayers: number;
}

const HomePage: React.FC<HomePageProps> = ({
    isAdmin,
    launcherUpdateState,
    downloadProgress,
    onSettingsClick,
    onStartUpdate,
    onlinePlayers,
    maxPlayers
}) => {
    const [newsPage, setNewsPage] = useState(1);
    const [changelogPage, setChangelogPage] = useState(1);
    const [eventsPage, setEventsPage] = useState(1);
    const [isLaunching, setIsLaunching] = useState(false);
    const [launchError, setLaunchError] = useState<string | null>(null);

    const handleStartGame = async () => {
        try {
            setIsLaunching(true);
            setLaunchError(null);
            console.log('Starting game...');

            const result = await bridge.launchGame();
            console.log('Game launch result:', result);

            if (!result.success) {
                setLaunchError(result.message);
            }
        } catch (error) {
            console.error('Failed to launch game:', error);
            setLaunchError(String(error));
        } finally {
            setIsLaunching(false);
        }
    };

    const isUpdateMode = launcherUpdateState === 'update_required' || launcherUpdateState === 'downloading';
    const isDownloading = launcherUpdateState === 'downloading';

    return (
        <BackgroundShell>
            <StatusHeader
                onlinePlayers={onlinePlayers}
                maxPlayers={maxPlayers}
                downloadProgress={isDownloading ? downloadProgress : undefined}
            />
            <section className="hero">
                <h1 className="hero-title">OPAL MU Core – Season 6</h1>
                <p className="hero-subtitle">
                    Enter Opal MU, a server created for true MU veterans and passionate adventurers who enjoy the effort
                    and glory of a slow but rewarding game. Based on highly stable and refined S6 files, developed by the
                    GMs of MUPLC and the Admin of PantherMU, our server offers a classic yet polished MU Online
                    experience.
                </p>
                <div className="hero-actions">
                    {isUpdateMode ? (
                        <button
                            className="hero-button hero-button-update"
                            onClick={onStartUpdate}
                            disabled={isDownloading}
                        >
                            <HiArrowDown size={18} />
                            <span>{isDownloading ? `Updating... ${downloadProgress || 0}%` : 'UPDATE LAUNCHER'}</span>
                        </button>
                    ) : (
                        <button
                            className="hero-button hero-button-primary"
                            onClick={handleStartGame}
                            disabled={isLaunching}
                        >
                            <HiPlay size={18} />
                            <span>{isLaunching ? 'LAUNCHING...' : 'START GAME'}</span>
                        </button>
                    )}
                    <button className="hero-button hero-button-secondary" onClick={onSettingsClick}>
                        <HiCog6Tooth size={18} />
                        <span>SETTINGS</span>
                    </button>
                    {isAdmin && (
                        <button className="hero-button hero-button-admin">
                            <span>AdminCP</span>
                        </button>
                    )}
                </div>
                {launchError && (
                    <div className="launch-error">
                        {launchError}
                    </div>
                )}
            </section>
            <section className="home-panels">
                {/* Latest News */}
                <article className="glass-panel home-panel">
                    <div className="panel-header"><span className="panel-title"><span>📰</span> LATEST NEWS</span></div>
                    <div className="panel-body">
                        <div className="news-item"><h4>Season 18 Launch!</h4><p>The new season is here with incredible rewards and challenges.</p></div>
                        <div className="news-item"><h4>Castle Siege Event</h4><p>Register your guild for the ultimate battle this weekend.</p></div>
                        <div className="news-item"><h4>Double EXP Weekend</h4><p>Level up faster with our special experience boost event.</p></div>
                    </div>
                    <div className="panel-footer">
                        <button className={newsPage === 1 ? 'page-btn active' : 'page-btn'} onClick={() => setNewsPage(1)}>1</button>
                        <button className={newsPage === 2 ? 'page-btn active' : 'page-btn'} onClick={() => setNewsPage(2)}>2</button>
                        <button className="page-btn">&gt;</button>
                    </div>
                </article>
                {/* Changelogs */}
                <article className="glass-panel home-panel">
                    <div className="panel-header"><span className="panel-title"><span>🔄</span> CHANGELOGS</span></div>
                    <div className="panel-body">
                        <div className="news-item"><h4>Patch v13.1</h4><p>Improved MG and RE PvP performance balance.</p></div>
                        <div className="news-item"><h4>New AntiCheat Update</h4><p>Detects macro tools and illegal third‑party software.</p></div>
                        <div className="news-item"><h4>Shop Visual Update</h4><p>Item tooltips now show full stats and bonuses.</p></div>
                    </div>
                    <div className="panel-footer">
                        <button className={changelogPage === 1 ? 'page-btn active' : 'page-btn'} onClick={() => setChangelogPage(1)}>1</button>
                        <button className={changelogPage === 2 ? 'page-btn active' : 'page-btn'} onClick={() => setChangelogPage(2)}>2</button>
                        <button className="page-btn">&gt;</button>
                    </div>
                </article>
                {/* Events */}
                <article className="glass-panel home-panel">
                    <div className="panel-header"><span className="panel-title"><span>📅</span> EVENTS</span></div>
                    <div className="panel-body">
                        <div className="news-item"><h4>Golden Invasion</h4><p>Every day at 18:00 - defeat golden monsters for Bless.</p></div>
                        <div className="news-item"><h4>Castle Siege</h4><p>Sunday 18:00 - Fight for domination and receive unique rewards.</p></div>
                        <div className="news-item"><h4>Blood Castle Frenzy</h4><p>Extra jewel of chaos drop chance this week.</p></div>
                    </div>
                    <div className="panel-footer">
                        <button className={eventsPage === 1 ? 'page-btn active' : 'page-btn'} onClick={() => setEventsPage(1)}>1</button>
                        <button className={eventsPage === 2 ? 'page-btn active' : 'page-btn'} onClick={() => setEventsPage(2)}>2</button>
                        <button className="page-btn">&gt;</button>
                    </div>
                </article>
            </section>
        </BackgroundShell>
    );
};

export default HomePage;
