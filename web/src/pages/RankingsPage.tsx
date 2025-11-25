import React, { useState } from 'react';
import './RankingsPage.css';

const RankingsPage: React.FC = () => {
    const [activeCategory, setActiveCategory] = useState('general');

    const categories = [
        { id: 'general', label: 'General' },
        { id: 'online', label: 'Online' },
        { id: 'pvp', label: 'PvP' }, { id: 'guilds', label: 'Guilds' },
        { id: 'elo', label: 'ELO' },
    ];

    return (
        <div className="rankings-page">
            <h1 className="page-title">Player Rankings</h1>

            {/* Category Tabs */}
            <div className="category-tabs">
                {categories.map((cat) => (
                    <button
                        key={cat.id}
                        className={`category-tab ${activeCategory === cat.id ? 'active' : ''}`}
                        onClick={() => setActiveCategory(cat.id)}
                    >
                        {cat.label}
                    </button>
                ))}
            </div>

            {/* Filters */}
            <div className="filters">
                <select className="filter-select">
                    <option>All Classes</option>
                    <option>Dark Knight</option>
                    <option>Dark Wizard</option>
                    <option>Elf</option>
                </select>

                <input
                    type="text"
                    className="filter-search"
                    placeholder="Search player..."
                />
            </div>

            {/* Rankings Table */}
            <div className="rankings-table">
                <table>
                    <thead>
                        <tr>
                            <th>Position</th>
                            <th>Class</th>
                            <th>Name</th>
                            <th>GR</th>
                            <th>RR</th>
                            <th>LVL</th>
                        </tr>
                    </thead>
                    <tbody>
                        {[1, 2, 3, 4, 5, 6, 7].map((rank) => (
                            <tr key={rank}>
                                <td>
                                    <div className="rank-cell">
                                        <span className={`rank-dot ${rank <= 3 ? 'top' : ''}`}></span>
                                        <span>{rank}</span>
                                    </div>
                                </td>
                                <td>
                                    <div className="class-icon">🛡️</div>
                                </td>
                                <td className="name-cell">Player{rank}</td>
                                <td>0</td>
                                <td>{5 - Math.floor(rank / 2)}</td>
                                <td>400</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Pagination */}
            <div className="pagination">
                <button className="page-btn">&lt;</button>
                <button className="page-btn active">1</button>
                <button className="page-btn">2</button>
                <button className="page-btn">...</button>
                <button className="page-btn">4</button>
                <button className="page-btn">&gt;</button>
            </div>
        </div>
    );
};

export default RankingsPage;
