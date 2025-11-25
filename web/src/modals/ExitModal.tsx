import React from 'react';
import './ExitModal.css';

interface ExitModalProps {
    onCancel: () => void;
    onConfirm: () => void;
}

const ExitModal: React.FC<ExitModalProps> = ({ onCancel, onConfirm }) => {
    return (
        <div className="modal-overlay" onClick={onCancel}>
            <div className="modal-content exit-modal" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>Exit Launcher?</h2>
                </div>

                <div className="modal-body">
                    <p>Are you sure you want to close the launcher?</p>
                </div>

                <div className="modal-footer">
                    <button className="btn btn-secondary" onClick={onCancel}>Cancel</button>
                    <button className="btn btn-primary" onClick={onConfirm}>Exit</button>
                </div>
            </div>
        </div>
    );
};

export default ExitModal;
