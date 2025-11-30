import React, { useState, useEffect } from 'react';
import { HiXMark } from 'react-icons/hi2';
import { bridge, SUPPORTED_RESOLUTIONS, type Settings } from '../services/bridge';
import './SettingsModal.css';

interface SettingsModalProps {
    onClose: () => void;
}

const LANGUAGES = [
    { code: 'en', label: 'English' },
    { code: 'es', label: 'Spanish' },
    { code: 'ko', label: 'Korean' },
    { code: 'pt', label: 'Portuguese' }
];

const SettingsModal: React.FC<SettingsModalProps> = ({ onClose }) => {
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Settings state
    const [resolution, setResolution] = useState('1366x768');
    const [windowMode, setWindowMode] = useState(true);
    const [music, setMusic] = useState(true);
    const [sound, setSound] = useState(true);
    const [language, setLanguage] = useState('en');

    // Load settings on mount
    useEffect(() => {
        const loadSettings = async () => {
            try {
                setIsLoading(true);
                const settings = await bridge.getSettings();

                setResolution(settings.resolution || '1366x768');
                setWindowMode(settings.window_mode !== false);
                setMusic(settings.music !== false);
                setSound(settings.sound !== false);
                setLanguage(settings.language || 'en');

                console.log('Settings loaded:', settings);
            } catch (err) {
                console.error('Failed to load settings:', err);
                setError('Failed to load settings');
            } finally {
                setIsLoading(false);
            }
        };

        loadSettings();
    }, []);

    const handleSave = async () => {
        try {
            setIsSaving(true);
            setError(null);

            // Build settings object
            const settings: Settings = {
                language,
                resolution,
                window_mode: windowMode,
                sound,
                music
            };

            // Save settings to config.json
            const saveSuccess = await bridge.saveSettings(settings);

            if (!saveSuccess) {
                setError('Failed to save settings');
                return;
            }

            // Apply resolution change to the window
            const [widthStr, heightStr] = resolution.split('x');
            const width = parseInt(widthStr, 10);
            const height = parseInt(heightStr, 10);

            if (!isNaN(width) && !isNaN(height)) {
                await bridge.setResolution(width, height, windowMode);
            }

            console.log('Settings saved successfully');
            onClose();
        } catch (err) {
            console.error('Failed to save settings:', err);
            setError('Failed to save settings');
        } finally {
            setIsSaving(false);
        }
    };

    if (isLoading) {
        return (
            <div className="modal-overlay" onClick={onClose}>
                <div className="modal-content settings-modal" onClick={(e) => e.stopPropagation()}>
                    <div className="modal-header">
                        <h2>Settings</h2>
                        <button className="close-btn" onClick={onClose}>
                            <HiXMark size={24} />
                        </button>
                    </div>
                    <div className="modal-body">
                        <p>Loading settings...</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content settings-modal" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>Settings</h2>
                    <button className="close-btn" onClick={onClose}>
                        <HiXMark size={24} />
                    </button>
                </div>

                <div className="modal-body">
                    {error && (
                        <div className="setting-error">
                            {error}
                        </div>
                    )}

                    <div className="setting-field">
                        <label>Resolution:</label>
                        <select
                            className="setting-input"
                            value={resolution}
                            onChange={(e) => setResolution(e.target.value)}
                        >
                            {SUPPORTED_RESOLUTIONS.map((res) => (
                                <option key={res} value={res}>
                                    {res}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="setting-field checkbox-field">
                        <input
                            type="checkbox"
                            id="windowMode"
                            checked={windowMode}
                            onChange={(e) => setWindowMode(e.target.checked)}
                        />
                        <label htmlFor="windowMode">Windowed Mode</label>
                    </div>

                    <div className="setting-field checkbox-field">
                        <input
                            type="checkbox"
                            id="bgMusic"
                            checked={music}
                            onChange={(e) => setMusic(e.target.checked)}
                        />
                        <label htmlFor="bgMusic">Enable Background Music</label>
                    </div>

                    <div className="setting-field checkbox-field">
                        <input
                            type="checkbox"
                            id="sfx"
                            checked={sound}
                            onChange={(e) => setSound(e.target.checked)}
                        />
                        <label htmlFor="sfx">Enable Sound Effects</label>
                    </div>

                    <div className="setting-field">
                        <label>GUI Language:</label>
                        <select
                            className="setting-input"
                            value={language}
                            onChange={(e) => setLanguage(e.target.value)}
                        >
                            {LANGUAGES.map((lang) => (
                                <option key={lang.code} value={lang.code}>
                                    {lang.label}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                <div className="modal-footer">
                    <button className="btn btn-secondary" onClick={onClose} disabled={isSaving}>
                        Cancel
                    </button>
                    <button className="btn btn-primary" onClick={handleSave} disabled={isSaving}>
                        {isSaving ? 'Saving...' : 'Save'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default SettingsModal;
