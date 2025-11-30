# Event Notification Sound

This directory should contain the event notification sound file.

## Required File

- **Filename**: `event-notify.mp3`
- **Purpose**: Played when an unmuted event reaches its notification threshold (60 seconds before start)
- **Format**: MP3 audio file
- **Recommended**: Short notification sound (1-2 seconds), medium volume

## Usage

The sound is referenced in `web/src/hooks/useEventSound.ts` and will be played automatically when:
1. An event is unmuted (user has enabled notifications for that specific event)
2. The event is within 60 seconds of starting
3. The notification hasn't been fired yet for that event

## Note

Until a real sound file is added, the audio system will fail silently with a warning in the console.
You can add any `.mp3` file here named `event-notify.mp3` to enable sound notifications.
