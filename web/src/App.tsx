import { useState, useEffect } from 'react';
import HomePage from './pages/HomePage';
import RankingsPage from './pages/RankingsPage';
import GuidesPage from './pages/GuidesPage';
import EventsPage from './pages/EventsPage';
import DonatePage from './pages/DonatePage';
import SettingsModal from './modals/SettingsModal';
import ExitModal from './modals/ExitModal';
import './App.css';

function App() {
    const isAdmin = true; // Set true to show AdminCP button
    const launcherUpdateState: 'update_required' | 'downloading' = 'downloading';
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);
    const [isExitModalOpen, setIsExitModalOpen] = useState(false);
    const [currentView, setCurrentView] = useState('home');

    useEffect(() => {
        // Expose navigation function to window for Qt to call
        (window as any).navigateTo = (view: string) => {
            console.log(`Navigating to: ${view}`);
            setCurrentView(view);
        };
    }, []);

    const handleExitConfirm = () => {
        console.log('Exit confirmed - would close launcher here');
        setIsExitModalOpen(false);
    };

    const renderContent = () => {
        switch (currentView) {
            case 'home':
                return (
                    <HomePage
                        isAdmin={isAdmin}
                        launcherUpdateState={launcherUpdateState}
                        onSettingsClick={() => setIsSettingsOpen(true)}
                    />
                );
            case 'rankings':
                return <RankingsPage />;
            case 'guides':
                return <GuidesPage />;
            case 'events':
                return <EventsPage />;
            case 'donate':
                return <DonatePage />;
            default:
                return (
                    <HomePage
                        isAdmin={isAdmin}
                        launcherUpdateState={launcherUpdateState}
                        onSettingsClick={() => setIsSettingsOpen(true)}
                    />
                );
        }
    };

    return (
        <div id="launcher-root" className="launcher-root">
            {/* Sidebar is now rendered in Qt - React only handles content */}
            <main className="react-content">
                {renderContent()}
            </main>

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
