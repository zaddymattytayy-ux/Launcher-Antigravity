import React from 'react';
import { HiXMark } from 'react-icons/hi2';
import './SettingsModal.css';

interface SettingsModalProps {
    onClose: () => void;
}

const SettingsModal: React.FC<SettingsModalProps> = ({ onClose }) => {
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
                    <div className="setting-field">
                        <label>Resolution:</label>
                        <select className="setting-input">
                            <option>1366x768 16:9 (Best)</option>
                            <option>1920x1080 16:9</option>
                            <option>2560x1440 16:9</option>
                        </select>
                    </div>

                    <div className="setting-field checkbox-field">
                        <input type="checkbox" id="bgMusic" defaultChecked />
                        <label htmlFor="bgMusic">Enable Background Music</label>
                    </div>

                    <div className="setting-field checkbox-field">
                        <input type="checkbox" id="sfx" defaultChecked />
                        <label htmlFor="sfx">Enable Sound Effects</label>
                    </div>

                    <div className="setting-field">
                        <label>GUI Language:</label>
                        <select className="setting-input">
                            <option>English</option>
                            <option>Spanish</option>
                            <option>Korean</option>
                            <option>Portuguese</option>
                        </select>
                    </div>
                </div>

                <div className="modal-footer">
                    <button className="btn btn-secondary" onClick={onClose}>Cancel</button>
                    <button className="btn btn-primary" onClick={onClose}>Save</button>
                </div>
            </div>
        </div>
    );
};

export default SettingsModal;
