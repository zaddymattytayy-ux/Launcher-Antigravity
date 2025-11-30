import React from 'react';

interface BackgroundShellProps {
    children: React.ReactNode;
}

const BackgroundShell: React.FC<BackgroundShellProps> = ({ children }) => {
    return (
        <div className="home-root">
            <div className="home-bg" />
            <div className="home-content">
                {children}
            </div>
        </div>
    );
};

export default BackgroundShell;
