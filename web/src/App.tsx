import { useState } from 'react';
import HomePage from './pages/HomePage';
import SettingsModal from './modals/SettingsModal';
import ExitModal from './modals/ExitModal';
import './App.css';

function App() {
    const isAdmin = true; // Set true to show AdminCP button
    const launcherUpdateState: 'update_required' | 'downloading' = 'downloading';
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);
    const [isExitModalOpen, setIsExitModalOpen] = useState(false);

    const handleExitConfirm = () => {
        console.log('Exit confirmed - would close launcher here');
        setIsExitModalOpen(false);
    };

    return (
        <div id="launcher-root" className="launcher-root">
            {/* Sidebar is now rendered in Qt - React only handles content */}
            <main className="react-content">
                <HomePage
                    isAdmin={isAdmin}
                    launcherUpdateState={launcherUpdateState}
                    onSettingsClick={() => setIsSettingsOpen(true)}
                />
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
