import threading
import time
import requests
import json
from datetime import datetime, timedelta
from PyQt6.QtCore import QObject, pyqtSignal

class EventTimerService(QObject):
    # Signals
    eventUpdated = pyqtSignal(str)  # Emits JSON string with event updates
    eventNotification = pyqtSignal(str, int)  # Emits (event_name, minutes_until)
    
    def __init__(self, settings_manager=None):
        super().__init__()
        self.settings = settings_manager
        self.events = []
        self.running = False
        self.thread = None
        self.notified_events = set()  # Track which events we've notified about
        
    def start(self):
        """Start the background event timer thread"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_timer, daemon=True)
            self.thread.start()
            print("Event timer service started")
    
    def stop(self):
        """Stop the background event timer thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
        print("Event timer service stopped")
    
    def fetch_events(self):
        """Fetch events from the API"""
        try:
            api_url = "http://localhost/CustomLauncher/api/events.php"
            if self.settings:
                api_url = self.settings.get("api_url", "http://localhost/CustomLauncher/api/") + "../events.php"
            
            response = requests.get(api_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.events = data.get('events', [])
                print(f"Loaded {len(self.events)} events from API")
                return True
        except Exception as e:
            print(f"Error fetching events: {e}")
            # Use fallback events if API fails
            self._load_fallback_events()
        return False
    
    def _load_fallback_events(self):
        """Load fallback events if API is unavailable"""
        self.events = [
            {
                'name': 'Blood Castle',
                'time': '00:00',
                'days': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                'category': 'Mini-Game'
            },
            {
                'name': 'Devil Square',
                'time': '01:00',
                'days': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                'category': 'Mini-Game'
            },
            {
                'name': 'Chaos Castle',
                'time': '02:00',
                'days': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                'category': 'PvP'
            }
        ]
    
    def _run_timer(self):
        """Background thread that updates events every second"""
        # Initial fetch
        self.fetch_events()
        
        while self.running:
            try:
                # Calculate upcoming events
                upcoming = self.get_upcoming_events()
                
                # Emit update signal
                self.eventUpdated.emit(json.dumps(upcoming))
                
                # Check for 5-minute notifications
                self._check_notifications(upcoming)
                
                # Sleep for 1 second
                time.sleep(1)
                
            except Exception as e:
                print(f"Error in event timer loop: {e}")
                time.sleep(1)
    
    def get_upcoming_events(self):
        """Calculate and return upcoming events with countdown"""
        now = datetime.now()
        current_day = now.strftime('%a')  # Mon, Tue, etc.
        
        upcoming = []
        
        for event in self.events:
            # Check if event runs today
            if current_day not in event.get('days', []):
                continue
            
            # Parse event time
            event_time_str = event.get('time', '00:00')
            try:
                hour, minute = map(int, event_time_str.split(':'))
                event_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # If event time has passed today, skip it
                if event_time < now:
                    continue
                
                # Calculate time until event
                time_until = event_time - now
                seconds_until = int(time_until.total_seconds())
                
                upcoming.append({
                    'name': event['name'],
                    'category': event.get('category', 'Event'),
                    'time': event_time_str,
                    'seconds_until': seconds_until,
                    'time_until_str': self._format_time_until(seconds_until),
                    'status': 'upcoming'
                })
                
            except Exception as e:
                print(f"Error parsing event time for {event.get('name')}: {e}")
        
        # Sort by time until (closest first)
        upcoming.sort(key=lambda x: x['seconds_until'])
        
        return upcoming
    
    def _format_time_until(self, seconds):
        """Format seconds into human-readable string"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes}m {secs}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"
    
    def _check_notifications(self, upcoming_events):
        """Check if any events need 5-minute notification"""
        for event in upcoming_events:
            seconds_until = event['seconds_until']
            event_name = event['name']
            
            # Check if event is 5 minutes away (300 seconds ± 2 seconds tolerance)
            if 298 <= seconds_until <= 302:
                # Create unique key for this event occurrence
                event_key = f"{event_name}_{event['time']}"
                
                # Only notify once per event occurrence
                if event_key not in self.notified_events:
                    self.notified_events.add(event_key)
                    self.eventNotification.emit(event_name, 5)
                    print(f"5-minute notification: {event_name}")
                    
                    # Play sound notification (optional)
                    self._play_notification_sound()
            
            # Clean up old notifications (events that have passed)
            elif seconds_until > 310:
                event_key = f"{event_name}_{event['time']}"
                self.notified_events.discard(event_key)
    
    def _play_notification_sound(self):
        """Play a notification sound"""
        try:
            # Use Windows beep
            import winsound
            winsound.Beep(1000, 200)  # 1000 Hz for 200ms
        except Exception as e:
            print(f"Could not play notification sound: {e}")
    
    def get_next_event(self):
        """Get the next upcoming event"""
        upcoming = self.get_upcoming_events()
        return upcoming[0] if upcoming else None
    
    def refresh_events(self):
        """Manually refresh events from API"""
        return self.fetch_events()
