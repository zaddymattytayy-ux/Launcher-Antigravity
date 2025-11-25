import React from 'react';

interface IconButtonProps {
    icon: React.ComponentType<{ size?: number | string }>;
    label: string;
    active?: boolean;
    onClick?: () => void;
}

const IconButton: React.FC<IconButtonProps> = ({ icon: Icon, label, active = false, onClick }) => {
    return (
        <button
            type="button"
            className={`icon-button ${active ? 'is-active' : ''}`}
            onClick={onClick}
            aria-label={label}
            title={label}
        >
            <Icon size={22} />
        </button>
    );
};

export default IconButton;
