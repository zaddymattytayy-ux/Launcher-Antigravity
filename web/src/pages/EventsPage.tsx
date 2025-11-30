import React, { useState, useEffect } from 'react';
import './EventsPage.css';
import BackgroundShell from '../components/layout/BackgroundShell';
import StatusHeader from '../components/layout/StatusHeader';
import { useEventTimers, type LauncherEvent } from '../hooks/useEventTimers';
import { useEventSound, useEventNotifications } from '../hooks/useEventSound';
import { HiBellAlert, HiBellSlash } from 'react-icons/hi2';
import { bridge } from '../services/bridge';

type EventCategory = 'events' | 'invasions' | 'bosses' | 'others';

interface EventsPageProps {
    onlinePlayers?: number;
    maxPlayers?: number;
}

const EventsPage: React.FC<EventsPageProps> = ({
    onlinePlayers = 1,
    maxPlayers = 500
}) => {
    const [activeCategory, setActiveCategory] = useState<EventCategory>('events');
    const [muteState, setMuteState] = useState<Record<string, boolean>>({});
    const [selectedEvent, setSelectedEvent] = useState<string | null>(null);
    const [currentPage, setCurrentPage] = useState<number>(1);
    const EVENTS_PER_PAGE = 7;
    // Fix #5: Global mute state - when true, no sounds play regardless of per-event settings
    const [globalMuteAll, setGlobalMuteAll] = useState<boolean>(true);

    // Mock event data - will be replaced by Python service when available
    const [allEvents, setAllEvents] = useState<LauncherEvent[]>([
        {
            id: 'event-1',
            name: 'Golden Invasion',
            category: 'events',
            nextStart: new Date(Date.now() + 13 * 60 * 1000 + 22 * 1000).toISOString(),
            description: 'Golden monsters invade with special rewards'
        },
        {
            id: 'event-2',
            name: 'Castle Siege',
            category: 'events',
            nextStart: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(),
            description: 'Epic guild battle for castle control'
        },
        {
            id: 'event-3',
            name: 'Chaos Castle',
            category: 'events',
            nextStart: new Date(Date.now() + 3 * 60 * 60 * 1000).toISOString(),
            description: 'Battle in the Chaos Castle arena'
        },
        {
            id: 'event-4',
            name: 'Devil Square',
            category: 'events',
            nextStart: new Date(Date.now() + 4 * 60 * 60 * 1000).toISOString(),
            description: 'Enter Devil Square for great rewards'
        },
        {
            id: 'event-5',
            name: 'Blood Castle',
            category: 'events',
            nextStart: new Date(Date.now() + 5 * 60 * 60 * 1000).toISOString(),
            description: 'Conquer Blood Castle for exclusive items'
        },
        {
            id: 'event-6',
            name: 'Imperial Guardian',
            category: 'events',
            nextStart: new Date(Date.now() + 6 * 60 * 60 * 1000).toISOString(),
            description: 'Defend against the Imperial Guardian'
        },
        {
            id: 'event-7',
            name: 'Tormented Square',
            category: 'events',
            nextStart: new Date(Date.now() + 7 * 60 * 60 * 1000).toISOString(),
            description: 'Fight in the Tormented Square'
        },
        {
            id: 'event-8',
            name: 'Illusion Temple',
            category: 'events',
            nextStart: new Date(Date.now() + 8 * 60 * 60 * 1000).toISOString(),
            description: 'Team battle in Illusion Temple'
        },
        {
            id: 'event-9',
            name: 'Doppelganger',
            category: 'events',
            nextStart: new Date(Date.now() + 9 * 60 * 60 * 1000).toISOString(),
            description: 'Defeat your doppelganger for rewards'
        },
        {
            id: 'event-10',
            name: 'Kanturu Event',
            category: 'events',
            nextStart: new Date(Date.now() + 10 * 60 * 60 * 1000).toISOString(),
            description: 'Participate in the Kanturu event'
        },
        {
            id: 'inv-1',
            name: 'White Wizard Invasion',
            category: 'invasions',
            nextStart: new Date(Date.now() + 45 * 60 * 1000).toISOString(),
            description: 'White Wizard spawns with rare drops'
        },
        {
            id: 'inv-2',
            name: 'Red Dragon Invasion',
            category: 'invasions',
            nextStart: new Date(Date.now() + 3 * 60 * 60 * 1000).toISOString(),
            description: 'Powerful dragon invasion event'
        },
        {
            id: 'boss-1',
            name: 'Medusa Spawn',
            category: 'bosses',
            nextStart: new Date(Date.now() + 30 * 60 * 1000).toISOString(),
            description: 'Medusa boss appears in Tarkan'
        },
        {
            id: 'boss-2',
            name: 'Kundun Awakening',
            category: 'bosses',
            nextStart: new Date(Date.now() + 4 * 60 * 60 * 1000).toISOString(),
            description: 'Ancient beast awakens'
        },
        {
            id: 'other-1',
            name: 'Happy Hour',
            category: 'others',
            nextStart: new Date(Date.now() + 20 * 60 * 1000).toISOString(),
            description: 'Double experience and drop rates'
        },
        {
            id: 'other-2',
            name: 'Blood Castle',
            category: 'others',
            nextStart: new Date(Date.now() + 90 * 60 * 1000).toISOString(),
            description: 'Enter Blood Castle for exclusive rewards'
        }
    ]);

    const timers = useEventTimers(allEvents);
    const { play } = useEventSound({ enabled: true });
    const { markAsNotified, hasBeenNotified } = useEventNotifications();

    // Subscribe to Python event updates when available
    useEffect(() => {
        const subscribeToEvents = async () => {
            try {
                await bridge.onEventUpdated((events) => {
                    console.log('Received events from Python:', events);
                    // Only replace if we got valid data
                    if (Array.isArray(events) && events.length > 0) {
                        // Transform events to match our LauncherEvent structure
                        const transformedEvents: LauncherEvent[] = events.map((event: any, index: number) => ({
                            id: event.id || `event-${index}`,
                            name: event.name || 'Unknown Event',
                            category: event.category || 'events',
                            nextStart: event.nextStart || event.time || new Date().toISOString(),
                            description: event.description || ''
                        }));
                        setAllEvents(transformedEvents);
                    }
                });
            } catch (error) {
                console.error('Failed to subscribe to events:', error);
            }
        };

        subscribeToEvents();
    }, []);

    // Initialize all events as muted, or load from localStorage
    useEffect(() => {
        const stored = localStorage.getItem('launcher_event_mutes');
        if (stored) {
            try {
                setMuteState(JSON.parse(stored));
            } catch (e) {
                console.warn('Failed to parse stored mute state');
            }
        } else {
            // Default all to muted
            const initialMuteState: Record<string, boolean> = {};
            allEvents.forEach(event => {
                initialMuteState[event.id] = true;
            });
            setMuteState(initialMuteState);
        }
    }, [allEvents]);

    // Save mute state to localStorage whenever it changes
    useEffect(() => {
        if (Object.keys(muteState).length > 0) {
            localStorage.setItem('launcher_event_mutes', JSON.stringify(muteState));
        }
    }, [muteState]);

    // Check for events hitting notification threshold (60 seconds before start)
    // Fix #5: Sound only plays when: event unmuted AND global mute disabled AND threshold reached
    useEffect(() => {
        const NOTIFICATION_THRESHOLD = 60000; // 60 seconds in ms

        allEvents.forEach(event => {
            const timer = timers[event.id];
            if (!timer) return;

            const isUnmuted = muteState[event.id] === false;
            const shouldNotify = timer.remainingMs > 0 &&
                timer.remainingMs <= NOTIFICATION_THRESHOLD &&
                !hasBeenNotified(event.id);

            // Fix #5: Check both per-event mute AND global mute
            if (shouldNotify && isUnmuted && !globalMuteAll) {
                play();
                markAsNotified(event.id);
            }
        });
    }, [timers, muteState, allEvents, play, markAsNotified, hasBeenNotified, globalMuteAll]);

    const toggleMute = (eventId: string) => {
        setMuteState(prev => ({
            ...prev,
            [eventId]: !prev[eventId]
        }));
    };

    const toggleCategoryMuteAll = () => {
        const categoryEvents = allEvents.filter(e => e.category === activeCategory);
        const allMuted = categoryEvents.every(e => muteState[e.id] === true);

        const newState = { ...muteState };
        categoryEvents.forEach(event => {
            newState[event.id] = !allMuted;
        });
        setMuteState(newState);
    };

    // Fix #5: Toggle global mute - affects all events across all categories
    const toggleGlobalMute = () => {
        setGlobalMuteAll(prev => !prev);
    };

    const categories = [
        { id: 'events' as EventCategory, label: 'Events' },
        { id: 'invasions' as EventCategory, label: 'Invasions' },
        { id: 'bosses' as EventCategory, label: 'Bosses' },
        { id: 'others' as EventCategory, label: 'Others' }
    ];

    const filteredEvents = allEvents
        .filter(e => e.category === activeCategory)
        .sort((a, b) => {
            const timeA = timers[a.id]?.remainingMs ?? Infinity;
            const timeB = timers[b.id]?.remainingMs ?? Infinity;
            return timeA - timeB;
        });

    // Pagination logic
    const totalPages = Math.ceil(filteredEvents.length / EVENTS_PER_PAGE);
    const startIndex = (currentPage - 1) * EVENTS_PER_PAGE;
    const paginatedEvents = filteredEvents.slice(startIndex, startIndex + EVENTS_PER_PAGE);

    // Reset to page 1 when category changes
    useEffect(() => {
        setCurrentPage(1);
    }, [activeCategory]);

    const currentEvent = selectedEvent
        ? allEvents.find(e => e.id === selectedEvent)
        : paginatedEvents[0];

    return (
        <BackgroundShell>
            <StatusHeader onlinePlayers={onlinePlayers} maxPlayers={maxPlayers} />

            <section className="events-hero">
                <h1 className="events-title">Upcoming Events</h1>
                <p className="events-subtitle">Stay informed about server events and never miss important activities</p>
            </section>

            <div className="events-container">
                {/* Category Tabs */}
                <div className="events-header">
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
                    <div className="mute-controls">
                        <button
                            className={`global-mute-btn ${globalMuteAll ? 'muted' : ''}`}
                            onClick={toggleGlobalMute}
                            title={globalMuteAll ? 'Enable all sounds' : 'Disable all sounds'}
                        >
                            {globalMuteAll ? '🔇 Sounds Off' : '🔊 Sounds On'}
                        </button>
                        <button className="mute-all-btn" onClick={toggleCategoryMuteAll}>
                            {filteredEvents.every(e => muteState[e.id] === true) ? 'Unmute Category' : 'Mute Category'}
                        </button>
                    </div>
                </div>

                {/* Main Content */}
                <div className="events-content">
                    {/* Event List */}
                    <div className="glass-panel events-list">
                        <div className="list-header">
                            <h3 className="list-title">Upcoming {categories.find(c => c.id === activeCategory)?.label}</h3>
                            <div className="list-pagination">
                                <button
                                    className="page-btn"
                                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                                    disabled={currentPage === 1}
                                >
                                    &lt;
                                </button>
                                <button className="page-btn active">{currentPage}</button>
                                <button
                                    className="page-btn"
                                    onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                                    disabled={currentPage === totalPages}
                                >
                                    &gt;
                                </button>
                            </div>
                        </div>
                        <div className="event-items">
                            {paginatedEvents.length > 0 ? (
                                paginatedEvents.map(event => {
                                    const timer = timers[event.id];
                                    const isMuted = muteState[event.id] !== false;
                                    const isSelected = selectedEvent === event.id;

                                    // Format timer display in compact format
                                    let timeDisplay = '--:--';
                                    if (timer) {
                                        const hours = Math.floor(timer.remainingMs / (1000 * 60 * 60));
                                        const minutes = Math.floor((timer.remainingMs % (1000 * 60 * 60)) / (1000 * 60));
                                        if (timer.hasStarted) {
                                            timeDisplay = 'NOW';
                                        } else {
                                            timeDisplay = `${hours}h ${minutes.toString().padStart(2, '0')}m`;
                                        }
                                    }

                                    return (
                                        <div
                                            key={event.id}
                                            className={`event-item ${isSelected ? 'selected' : ''}`}
                                            onClick={() => setSelectedEvent(event.id)}
                                        >
                                            <div className="event-item-content">
                                                <div className="event-item-left">
                                                    <h4 className="event-name">{event.name}</h4>
                                                    {timer && (
                                                        <div className="event-timer">
                                                            {timer.hasStarted ? (
                                                                <span className="timer-started">Started</span>
                                                            ) : (
                                                                <span className="timer-countdown">
                                                                    Starts in: {timer.formattedTime}
                                                                </span>
                                                            )}
                                                        </div>
                                                    )}
                                                </div>
                                                <div className="event-item-right">
                                                    <button
                                                        className={`mute-btn ${isMuted ? 'muted' : 'unmuted'}`}
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            toggleMute(event.id);
                                                        }}
                                                        title={isMuted ? 'Unmute notifications' : 'Mute notifications'}
                                                    >
                                                        {isMuted ? (
                                                            <HiBellSlash size={16} />
                                                        ) : (
                                                            <HiBellAlert size={16} />
                                                        )}
                                                    </button>
                                                    <span className="event-time-display">{timeDisplay}</span>
                                                </div>
                                            </div>
                                        </div>
                                    );
                                })
                            ) : (
                                <div className="no-events">
                                    <p>No upcoming events in this category</p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Event Details */}
                    <div className="glass-panel event-details">
                        {currentEvent ? (
                            <>
                                <h3 className="details-title">{currentEvent.name}</h3>
                                <div className="details-content">
                                    <div className="detail-row">
                                        <span className="detail-label">Description:</span>
                                    </div>
                                    <p className="detail-description">{currentEvent.description || 'No description available'}</p>

                                    <div className="detail-row" style={{ marginTop: '16px' }}>
                                        <span className="detail-label">Drop Info:</span>
                                    </div>
                                    <ul className="drop-info-list">
                                        <li>Jewel of Chaos</li>
                                        <li>Guardian Angel</li>
                                        <li>Blood Bone</li>
                                    </ul>

                                    <div className="event-image-placeholder">
                                        <span>🎮</span>
                                        <span>Event Preview Image</span>
                                    </div>
                                </div>
                            </>
                        ) : (
                            <div className="no-selection">
                                <p>Select an event to view details</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </BackgroundShell>
    );
};

export default EventsPage;
