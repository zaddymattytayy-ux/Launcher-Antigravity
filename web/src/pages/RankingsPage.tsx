import React, { useState } from 'react';
import './RankingsPage.css';
import BackgroundShell from '../components/layout/BackgroundShell';
import StatusHeader from '../components/layout/StatusHeader';

const RankingsPage: React.FC = () => {
    const [activeCategory, setActiveCategory] = useState('general');
    const onlinePlayers = 1;
    const maxPlayers = 500;

    const categories = [
        { id: 'general', label: 'General' },
        { id: 'online', label: 'Online' },
        { id: 'pvp', label: 'PvP' },
        { id: 'guilds', label: 'Guilds' },
        { id: 'elo', label: 'ELO' },
    ];

    return (
        <BackgroundShell>
            <StatusHeader onlinePlayers={onlinePlayers} maxPlayers={maxPlayers} />

            <section className="rankings-hero">
                <h1 className="rankings-title">Player Rankings</h1>
                <p className="rankings-subtitle">Compete for glory and claim your spot among the legends</p>
            </section>

            <div className="rankings-container">
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
                <div className="glass-panel rankings-table">
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
                            {[1, 2, 3, 4, 5].map((rank) => (
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
        </BackgroundShell>
    );
};

export default RankingsPage;
