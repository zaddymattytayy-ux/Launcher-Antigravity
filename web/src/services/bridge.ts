declare global {
    interface Window {
        qt: any;
        QWebChannel: any;
        launcherBridge?: any;
    }
}

class BridgeService {
    private bridge: any = null;
    private initPromise: Promise<void>;

    constructor() {
        this.initPromise = this.initBridge();
    }

    private initBridge(): Promise<void> {
        return new Promise((resolve) => {
            if (window.qt && window.qt.webChannelTransport) {
                new window.QWebChannel(window.qt.webChannelTransport, (channel: any) => {
                    this.bridge = channel.objects.launcherBridge;
                    window.launcherBridge = this.bridge;
                    console.log("Bridge initialized");
                    resolve();
                });
            } else {
                console.warn("Qt WebChannel not found. Running in browser mode?");
                resolve(); // Resolve anyway to allow mock data fallback
            }
        });
    }

    async launchGame(resolution: string, windowMode: boolean) {
        await this.initPromise;
        if (this.bridge) {
            return await this.bridge.launchGame(resolution, windowMode ? "windowed" : "fullscreen");
        }
        console.log("Mock launch game:", resolution, windowMode);
        return true;
    }

    async getSettings() {
        await this.initPromise;
        if (this.bridge) {
            // The bridge might return a string or object depending on implementation
            // Assuming it returns a JSON string based on previous code
            const settings = await this.bridge.getSettings();
            return typeof settings === 'string' ? JSON.parse(settings) : settings;
        }
        return { resolution: "1920x1080", windowMode: true };
    }

    async getSession() {
        await this.initPromise;
        if (this.bridge) {
            const session = await this.bridge.getSession();
            return typeof session === 'string' ? JSON.parse(session) : session;
        }
        return { logged: true, username: "Admin", is_admin: true }; // Default mock for dev
    }

    async startDrag() {
        await this.initPromise;
        if (this.bridge && typeof this.bridge.startDrag === 'function') {
            try {
                this.bridge.startDrag();
            } catch (error) {
                console.warn("startDrag call failed", error);
            }
        }
    }

    async onEventUpdated(callback: (events: any[]) => void) {
        await this.initPromise;
        if (this.bridge) {
            this.bridge.eventUpdated.connect((eventsJson: string) => {
                const events = JSON.parse(eventsJson);
                callback(events);
            });
        } else {
            // Mock events for browser testing
            setTimeout(() => {
                callback([
                    { name: 'Blood Castle', category: 'Mini-Game', time: '00:00', time_until_str: '2h 30m' },
                    { name: 'Devil Square', category: 'Mini-Game', time: '01:00', time_until_str: '3h 15m' },
                    { name: 'Chaos Castle', category: 'PvP', time: '02:00', time_until_str: '4h 0m' },
                ]);
            }, 1000);
        }
    }
}

export const bridge = new BridgeService();
