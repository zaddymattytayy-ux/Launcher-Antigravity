import React from 'react';
import './StatusHeader.css';

interface StatusHeaderProps {
    onlinePlayers: number;
    maxPlayers: number;
    downloadProgress?: number; // 0-100, undefined when not downloading
}

const StatusHeader: React.FC<StatusHeaderProps> = ({ onlinePlayers, maxPlayers, downloadProgress }) => {
    const isDownloading = downloadProgress !== undefined && downloadProgress < 100;
    return (
        <div className="status-header flex justify-between items-center mb-4">
            <div className="online-pill flex items-center">
                <svg className="inline-block mr-2" width="16" height="16" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2a10 10 0 100 20 10 10 0 000-20zM11 6h2v6h-2V6zm0 8h2v2h-2v-2z" />
                </svg>
                <span>Online: {onlinePlayers}/{maxPlayers}</span>
            </div>
            <div className="downloading-pill flex items-center">
                {isDownloading ? (
                    <>
                        <svg className="inline-block mr-2" width="16" height="16" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 2a10 10 0 100 20 10 10 0 000-20zM13 13h-2V7h2v6zm0 4h-2v-2h2v2z" />
                        </svg>
                        <span>Downloading... {downloadProgress}%</span>
                        <div className="download-progress ml-2">
                            <div className="progress-bar" style={{ width: `${downloadProgress}%` }} />
                        </div>
                    </>
                ) : (
                    <span>Ready</span>
                )}
            </div>
        </div>
    );
};

export default StatusHeader;
