import React from 'react';

interface CharacterIconProps {
    name: string;
    level: number;
    cls: string;
}

const CharacterIcon: React.FC<CharacterIconProps> = ({ name, level, cls }) => {
    return (
        <div className="flex items-center gap-3">
            <div className="relative">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                    <span className="text-white font-bold text-lg">{name.substring(0, 2).toUpperCase()}</span>
                </div>
                <div className="absolute -bottom-1 -right-1 bg-yellow-500 text-black text-xs font-bold px-1.5 py-0.5 rounded">
                    {level}
                </div>
            </div>
            <div>
                <p className="text-white font-semibold">{name}</p>
                <p className="text-gray-400 text-sm">{cls}</p>
            </div>
        </div>
    );
};

export default CharacterIcon;
