import { useState, useEffect, useCallback } from 'react';
import HomePage from './pages/HomePage';
import RankingsPage from './pages/RankingsPage';
import GuidesPage from './pages/GuidesPage';
import EventsPage from './pages/EventsPage';
import DonatePage from './pages/DonatePage';
import SettingsModal from './modals/SettingsModal';
import ExitModal from './modals/ExitModal';
import { bridge } from './services/bridge';
import './App.css';

type UpdateState = 'idle' | 'checking' | 'update_available' | 'downloading' | 'finished' | 'error';

function App() {
    // Session state
    const [isAdmin, setIsAdmin] = useState(false);
    const [isLoading, setIsLoading] = useState(true);

    // Update state
    const [updateState, setUpdateState] = useState<UpdateState>('idle');
    const [, setUpdateVersion] = useState<string | null>(null);
    const [downloadProgress, setDownloadProgress] = useState<number>(0);
    const [updateError, setUpdateError] = useState<string | null>(null);

    // Online count
    const [onlinePlayers, setOnlinePlayers] = useState(1);
    const maxPlayers = 500;

    // Modal state
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);
    const [isExitModalOpen, setIsExitModalOpen] = useState(false);

    // Navigation state
    const [currentView, setCurrentView] = useState('home');

    // Initialize app and subscribe to bridge events
    useEffect(() => {
        const init = async () => {
            try {
                // Get session info
                const session = await bridge.getSession();
                setIsAdmin(session.is_admin);

                // Get online count
                const count = await bridge.getOnlineCount();
                setOnlinePlayers(count);

                // Subscribe to update signals
                await bridge.onUpdateAvailable((version) => {
                    console.log('Update available:', version);
                    setUpdateVersion(version);
                    setUpdateState('update_available');
                });

                await bridge.onDownloadProgress((progress) => {
                    console.log('Download progress:', progress);
                    setDownloadProgress(progress);
                    if (progress > 0 && progress < 100) {
                        setUpdateState('downloading');
                    }
                });

                await bridge.onUpdateError((error) => {
                    console.error('Update error:', error);
                    setUpdateError(error);
                    setUpdateState('error');
                });

                await bridge.onUpdateFinished(() => {
                    console.log('Update finished');
                    setUpdateState('finished');
                    setDownloadProgress(100);
                });

                // Subscribe to unmanaged process detection (just log for now)
                await bridge.onUnmanagedProcessDetected((process) => {
                    console.warn('Unmanaged game process detected:', process);
                    // Could show a toast/notification here in the future
                });

            } catch (error) {
                console.error('Failed to initialize app:', error);
            } finally {
                setIsLoading(false);
            }
        };

        init();

        // Expose navigation function to window for Qt to call
        (window as any).navigateTo = (view: string) => {
            console.log(`Navigating to: ${view}`);
            setCurrentView(view);
        };
    }, []);

    // Periodically update online count
    useEffect(() => {
        const interval = setInterval(async () => {
            try {
                const count = await bridge.getOnlineCount();
                setOnlinePlayers(count);
            } catch (error) {
                console.error('Failed to get online count:', error);
            }
        }, 30000); // Update every 30 seconds

        return () => clearInterval(interval);
    }, []);

    const handleExitConfirm = useCallback(async () => {
        console.log('Exit confirmed - closing launcher');
        await bridge.exitLauncher();
        setIsExitModalOpen(false);
    }, []);

    const handleStartUpdate = useCallback(async () => {
        try {
            setUpdateState('downloading');
            setDownloadProgress(0);
            await bridge.startUpdate();
        } catch (error) {
            console.error('Failed to start update:', error);
            setUpdateState('error');
        }
    }, []);

    // Determine launcher update state for HomePage
    const getLauncherUpdateState = (): 'update_required' | 'downloading' | undefined => {
        if (updateState === 'update_available') {
            return 'update_required';
        }
        if (updateState === 'downloading') {
            return 'downloading';
        }
        return undefined;
    };

    const renderContent = () => {
        switch (currentView) {
            case 'home':
                return (
                    <HomePage
                        isAdmin={isAdmin}
                        launcherUpdateState={getLauncherUpdateState()}
                        downloadProgress={downloadProgress}
                        onSettingsClick={() => setIsSettingsOpen(true)}
                        onStartUpdate={handleStartUpdate}
                        onlinePlayers={onlinePlayers}
                        maxPlayers={maxPlayers}
                    />
                );
            case 'rankings':
                return <RankingsPage />;
            case 'guides':
                return <GuidesPage />;
            case 'events':
                return (
                    <EventsPage
                        onlinePlayers={onlinePlayers}
                        maxPlayers={maxPlayers}
                    />
                );
            case 'donate':
                return <DonatePage />;
            default:
                return (
                    <HomePage
                        isAdmin={isAdmin}
                        launcherUpdateState={getLauncherUpdateState()}
                        downloadProgress={downloadProgress}
                        onSettingsClick={() => setIsSettingsOpen(true)}
                        onStartUpdate={handleStartUpdate}
                        onlinePlayers={onlinePlayers}
                        maxPlayers={maxPlayers}
                    />
                );
        }
    };

    if (isLoading) {
        return (
            <div id="launcher-root" className="launcher-root">
                <main className="react-content" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <p style={{ color: '#fff' }}>Loading...</p>
                </main>
            </div>
        );
    }

    return (
        <div id="launcher-root" className="launcher-root">
            {/* Sidebar is now rendered in Qt - React only handles content */}
            <main className="react-content">
                {renderContent()}
            </main>

            {/* Update finished banner */}
            {updateState === 'finished' && (
                <div className="update-banner update-finished">
                    Update installed successfully. Please restart the launcher.
                </div>
            )}

            {/* Update error banner */}
            {updateState === 'error' && updateError && (
                <div className="update-banner update-error">
                    Update failed: {updateError}
                </div>
            )}

            {/* Modals */}
            {isSettingsOpen && <SettingsModal onClose={() => setIsSettingsOpen(false)} />}
            {isExitModalOpen && (
                <ExitModal
                    onCancel={() => setIsExitModalOpen(false)}
                    onConfirm={handleExitConfirm}
                />
            )}
        </div>
    );
}

export default App;
