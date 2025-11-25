import { useState } from 'react';
import HomePage from './pages/HomePage';
import RankingsPage from './pages/RankingsPage';
import DonatePage from './pages/DonatePage';
import GuidesPage from './pages/GuidesPage';
import EventsPage from './pages/EventsPage';
import SettingsModal from './modals/SettingsModal';
import ExitModal from './modals/ExitModal';
import Sidebar from './layout/Sidebar';
import './App.css';

type TabKey = 'home' | 'rankings' | 'donate' | 'guides' | 'events';

function App() {
    const isAdmin = true; // Set true to show AdminCP button
    const isGameInstalled = true; // Placeholder until hooked into real install detection
    const launcherUpdateState: 'update_required' | 'downloading' = 'downloading';
    const [activeTab, setActiveTab] = useState<TabKey>('home');
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);
    const [isExitModalOpen, setIsExitModalOpen] = useState(false);

    const handleExitConfirm = () => {
        console.log('Exit confirmed - would close launcher here');
        setIsExitModalOpen(false);
    };

    const renderContent = () => {
        switch (activeTab) {
        case 'rankings':
            return <RankingsPage />;
        case 'donate':
            return <DonatePage />;
        case 'guides':
            return <GuidesPage />;
        case 'events':
            return <EventsPage />;
        case 'home':
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
            <Sidebar
                activeTab={activeTab}
                onTabChange={setActiveTab}
                isGameInstalled={isGameInstalled}
                onExitClick={() => setIsExitModalOpen(true)}
            />

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
