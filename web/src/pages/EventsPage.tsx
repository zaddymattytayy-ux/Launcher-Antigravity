import React, { useEffect, useState } from 'react';
import GlassCard from '../components/GlassCard';
import { Clock, MapPin } from 'lucide-react';
import { bridge } from '../services/bridge';

interface Event {
    name: string;
    category: string;
    time: string;
    time_until_str?: string;
}

const EventsPage: React.FC = () => {
    const [events, setEvents] = useState<Event[]>([]);

    useEffect(() => {
        const connectEvents = async () => {
            await bridge.onEventUpdated((eventData) => {
                setEvents(eventData);
            });
        };
        connectEvents();
    }, []);

    return (
        <div className="p-6 space-y-8">
            <div className="text-center mb-8">
                <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-yellow-600 mb-3">
                    Event Schedule
                </h1>
                <p className="text-gray-300 text-lg">Upcoming events and their timers</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {events.length > 0 ? events.map((event, i) => (
                    <GlassCard key={i} className="hover:bg-white/15 transition-all">
                        <div className="flex items-start justify-between mb-4">
                            <div>
                                <h3 className="text-xl font-bold text-white mb-2">{event.name}</h3>
                                <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold bg-purple-500/20 text-purple-400">
                                    {event.category}
                                </span>
                            </div>
                            <Clock className="text-gray-400" size={24} />
                        </div>

                        <div className="space-y-2">
                            <div className="flex items-center gap-2 text-gray-300">
                                <MapPin size={16} />
                                <span className="text-sm">Starts at {event.time}</span>
                            </div>
                            {event.time_until_str && (
                                <div className="text-green-400 font-semibold">
                                    Starts in {event.time_until_str}
                                </div>
                            )}
                        </div>
                    </GlassCard>
                )) : (
                    <div className="col-span-full text-center text-gray-400 py-12">
                        <Clock size={48} className="mx-auto mb-4 opacity-50" />
                        <p>No upcoming events today</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default EventsPage;
