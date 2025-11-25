import React, { useState } from 'react';
import './GuidesPage.css';

const GuidesPage: React.FC = () => {
    const [activeCategory, setActiveCategory] = useState('search');
    const [selectedTopic, setSelectedTopic] = useState(1);

    const categories = [
        'Search', 'Game Start', 'Leveling & Farming', 'PvP Guide', 'Boss Guide',
        'Event Guide', 'Class Guide', 'Items & Equipment', 'Crafting & Economy',
        'Guild & Community', 'Tips & Tricks'
    ];

    const topics = [
        { id: 1, title: 'Welcome to Opal MU' },
        { id: 2, title: 'Character Creation & Classes' },
        { id: 3, title: 'Basic Controls & Interface' },
        { id: 4, title: 'First Steps in the Game' },
    ];

    return (
        <div className="guides-page">
            {/* Category Pills */}
            <div className="category-pills">
                {categories.map((cat) => (
                    <button
                        key={cat}
                        className={`category-pill ${activeCategory === cat.toLowerCase().replace(/\s+/g, '') ? 'active' : ''}`}
                        onClick={() => setActiveCategory(cat.toLowerCase().replace(/\s+/g, ''))}
                    >
                        {cat}
                    </button>
                ))}
            </div>

            {/* Two-Column Layout */}
            <div className="guides-content">
                {/* Left: Topics List */}
                <div className="topics-panel">
                    <div className="topics-list">
                        {topics.map((topic) => (
                            <div
                                key={topic.id}
                                className={`topic-item ${selectedTopic === topic.id ? 'active' : ''}`}
                                onClick={() => setSelectedTopic(topic.id)}
                            >
                                {topic.title}
                            </div>
                        ))}
                    </div>
                    <div className="topics-pagination">
                        <button className="page-btn active">1</button>
                        <button className="page-btn">2</button>
                        <button className="page-btn">&gt;</button>
                    </div>
                </div>

                {/* Right: Guide Content */}
                <div className="guide-panel">
                    <h2>Welcome to Opal MU</h2>
                    <p>
                        Welcome to the legendary world of MU Online. This  guide will help you understand the basics
                        of the game and get you started on your epic adventure through the MU continent.
                    </p>

                    <div className="guide-image">
                        <div className="image-placeholder">
                            🎮 MU Characters Illustration
                        </div>
                    </div>

                    <h3>Key Features</h3>
                    <ul>
                        <li><strong>Classes:</strong> Choose from several powerful character classes</li>
                        <li><strong>Leveling:</strong> Gain experience through quests and combat</li>
                        <li><strong>Equipment:</strong> Collect and upgrade powerful items</li>
                        <li><strong>PvP:</strong> Challenge other players in epic battles</li>
                    </ul>

                    <p>
                        Start your journey today and become a legend in the world of MU Online. May your adventures
                        be filled with glory and treasure!
                    </p>
                </div>
            </div>
        </div>
    );
};

export default GuidesPage;
