import { useEffect, useRef, useState } from 'react';

interface UseEventSoundOptions {
    enabled?: boolean;
    soundFile?: string;
}

export function useEventSound(options: UseEventSoundOptions = {}) {
    const { enabled = true, soundFile = '/notification.wav' } = options;
    const audioRef = useRef<HTMLAudioElement | null>(null);
    const [isReady, setIsReady] = useState(false);

    useEffect(() => {
        if (enabled) {
            audioRef.current = new Audio(soundFile);
            audioRef.current.volume = 0.75;

            // Preload the audio
            audioRef.current.load();
            audioRef.current.addEventListener('canplaythrough', () => {
                setIsReady(true);
            });
        }

        return () => {
            if (audioRef.current) {
                audioRef.current.pause();
                audioRef.current = null;
            }
        };
    }, [enabled, soundFile]);

    const play = () => {
        if (enabled && audioRef.current && isReady) {
            audioRef.current.currentTime = 0;
            audioRef.current.play().catch(err => {
                console.warn('Failed to play notification sound:', err);
            });
        }
    };

    return { play, isReady };
}

// Hook for tracking which events have already fired notifications
export function useEventNotifications() {
    const notifiedEvents = useRef(new Set<string>());

    const markAsNotified = (eventId: string) => {
        notifiedEvents.current.add(eventId);
    };

    const hasBeenNotified = (eventId: string): boolean => {
        return notifiedEvents.current.has(eventId);
    };

    const reset = () => {
        notifiedEvents.current.clear();
    };

    return { markAsNotified, hasBeenNotified, reset };
}
