import { useState, useEffect } from 'react';

export interface LauncherEvent {
    id: string;
    name: string;
    category: 'events' | 'invasions' | 'bosses' | 'others';
    nextStart: string; // ISO timestamp
    description?: string;
}

export interface EventTimerState {
    remainingMs: number;
    formattedTime: string;
    hasStarted: boolean;
}

export function useEventTimers(events: LauncherEvent[]): Record<string, EventTimerState> {
    const [timers, setTimers] = useState<Record<string, EventTimerState>>({});

    useEffect(() => {
        const updateTimers = () => {
            const now = Date.now();
            const newTimers: Record<string, EventTimerState> = {};

            events.forEach(event => {
                const startTime = new Date(event.nextStart).getTime();
                const remainingMs = startTime - now;
                const hasStarted = remainingMs <= 0;

                // Format time as "Xh Xm Xs"
                const absRemaining = Math.abs(remainingMs);
                const hours = Math.floor(absRemaining / (1000 * 60 * 60));
                const minutes = Math.floor((absRemaining % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((absRemaining % (1000 * 60)) / 1000);

                let formattedTime = '';
                if (hasStarted) {
                    formattedTime = 'Started';
                } else {
                    if (hours > 0) {
                        formattedTime = `${hours}h ${minutes}m ${seconds}s`;
                    } else if (minutes > 0) {
                        formattedTime = `${minutes}m ${seconds}s`;
                    } else {
                        formattedTime = `${seconds}s`;
                    }
                }

                newTimers[event.id] = {
                    remainingMs,
                    formattedTime,
                    hasStarted
                };
            });

            setTimers(newTimers);
        };

        // Initial update
        updateTimers();

        // Update every second
        const interval = setInterval(updateTimers, 1000);

        return () => clearInterval(interval);
    }, [events]);

    return timers;
}
