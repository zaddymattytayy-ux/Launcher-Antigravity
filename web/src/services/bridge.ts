declare global {
    interface Window {
        qt: any;
        QWebChannel: any;
        launcherBridge?: any;
    }
}

// Supported resolutions for the launcher
export const SUPPORTED_RESOLUTIONS = [
    '640x480',
    '800x600',
    '1024x768',
    '1280x1024',
    '1366x768',
    '1440x900',
    '1600x900',
    '1680x1050',
    '1920x1080'
] as const;

export type Resolution = typeof SUPPORTED_RESOLUTIONS[number];

export interface Settings {
    language: string;
    resolution: string;
    window_mode: boolean;
    sound: boolean;
    music: boolean;
    server_name?: string;
    version?: string;
    update_url?: string;
    api_url?: string;
    game_executable?: string;
    max_clients?: number;
    kill_unmanaged_clients?: boolean;
}

export interface Session {
    logged: boolean;
    username: string;
    is_admin: boolean;
}

export interface GameLaunchResult {
    success: boolean;
    message: string;
}

export interface UnmanagedProcess {
    pid: number;
    name: string;
}

class BridgeService {
    private bridge: any = null;
    private initPromise: Promise<void>;
    private _isInitialized = false;

    constructor() {
        this.initPromise = this.initBridge();
    }

    private initBridge(): Promise<void> {
        return new Promise((resolve) => {
            if (window.qt && window.qt.webChannelTransport) {
                new window.QWebChannel(window.qt.webChannelTransport, (channel: any) => {
                    this.bridge = channel.objects.launcherBridge;
                    window.launcherBridge = this.bridge;
                    this._isInitialized = true;
                    console.log("Bridge initialized successfully");
                    resolve();
                });
            } else {
                console.warn("Qt WebChannel not found. Running in browser mode with mocks.");
                this._isInitialized = false;
                resolve();
            }
        });
    }

    get isInitialized(): boolean {
        return this._isInitialized;
    }

    // ==================== Settings ====================

    async getSettings(): Promise<Settings> {
        await this.initPromise;
        if (this.bridge) {
            try {
                const settings = await this.bridge.getSettings();
                return typeof settings === 'string' ? JSON.parse(settings) : settings;
            } catch (error) {
                console.error('Failed to get settings:', error);
            }
        }
        // Default mock settings for browser development
        return {
            language: 'en',
            resolution: '1366x768',
            window_mode: true,
            sound: true,
            music: true,
            version: '1.0.0'
        };
    }

    async saveSettings(settings: Settings): Promise<boolean> {
        await this.initPromise;
        if (this.bridge) {
            try {
                return await this.bridge.saveSettings(JSON.stringify(settings));
            } catch (error) {
                console.error('Failed to save settings:', error);
                return false;
            }
        }
        console.log('Mock save settings:', settings);
        return true;
    }

    async setResolution(width: number, height: number, windowed: boolean): Promise<void> {
        await this.initPromise;
        if (this.bridge) {
            try {
                await this.bridge.setResolution(width, height, windowed);
            } catch (error) {
                console.error('Failed to set resolution:', error);
            }
        } else {
            console.log(`Mock set resolution: ${width}x${height}, windowed=${windowed}`);
        }
    }

    // ==================== Game Launch ====================

    async launchGame(): Promise<GameLaunchResult> {
        await this.initPromise;
        if (this.bridge) {
            try {
                const result = await this.bridge.launchGame();
                return typeof result === 'string' ? JSON.parse(result) : result;
            } catch (error) {
                console.error('Failed to launch game:', error);
                return { success: false, message: String(error) };
            }
        }
        console.log('Mock launch game');
        return { success: true, message: 'Mock launch successful' };
    }

    // ==================== Session ====================

    async getSession(): Promise<Session> {
        await this.initPromise;
        if (this.bridge) {
            try {
                const session = await this.bridge.getSession();
                return typeof session === 'string' ? JSON.parse(session) : session;
            } catch (error) {
                console.error('Failed to get session:', error);
            }
        }
        // Default mock session for dev
        return { logged: true, username: 'Admin', is_admin: true };
    }

    // ==================== Online Count ====================

    async getOnlineCount(): Promise<number> {
        await this.initPromise;
        if (this.bridge) {
            try {
                return await this.bridge.getOnlineCount();
            } catch (error) {
                console.error('Failed to get online count:', error);
            }
        }
        return 1; // Mock fallback
    }

    // ==================== Update System ====================

    async checkForUpdates(): Promise<void> {
        await this.initPromise;
        if (this.bridge) {
            try {
                await this.bridge.checkForUpdates();
            } catch (error) {
                console.error('Failed to check for updates:', error);
            }
        } else {
            console.log('Mock check for updates');
        }
    }

    async startUpdate(): Promise<void> {
        await this.initPromise;
        if (this.bridge) {
            try {
                await this.bridge.startUpdate();
            } catch (error) {
                console.error('Failed to start update:', error);
            }
        } else {
            console.log('Mock start update');
        }
    }

    async cancelUpdate(): Promise<void> {
        await this.initPromise;
        if (this.bridge) {
            try {
                await this.bridge.cancelUpdate();
            } catch (error) {
                console.error('Failed to cancel update:', error);
            }
        }
    }

    // ==================== Signal Subscriptions ====================

    async onUpdateAvailable(callback: (version: string) => void): Promise<void> {
        await this.initPromise;
        if (this.bridge && this.bridge.updateAvailable) {
            this.bridge.updateAvailable.connect(callback);
        } else {
            console.log('Mock: onUpdateAvailable subscribed');
        }
    }

    async onDownloadProgress(callback: (progress: number) => void): Promise<void> {
        await this.initPromise;
        if (this.bridge && this.bridge.downloadProgress) {
            this.bridge.downloadProgress.connect(callback);
        } else {
            console.log('Mock: onDownloadProgress subscribed');
        }
    }

    async onUpdateError(callback: (error: string) => void): Promise<void> {
        await this.initPromise;
        if (this.bridge && this.bridge.updateError) {
            this.bridge.updateError.connect(callback);
        } else {
            console.log('Mock: onUpdateError subscribed');
        }
    }

    async onUpdateFinished(callback: () => void): Promise<void> {
        await this.initPromise;
        if (this.bridge && this.bridge.updateFinished) {
            this.bridge.updateFinished.connect(callback);
        } else {
            console.log('Mock: onUpdateFinished subscribed');
        }
    }

    async onGameLaunched(callback: (success: boolean) => void): Promise<void> {
        await this.initPromise;
        if (this.bridge && this.bridge.gameLaunched) {
            this.bridge.gameLaunched.connect(callback);
        } else {
            console.log('Mock: onGameLaunched subscribed');
        }
    }

    async onEventUpdated(callback: (events: any[]) => void): Promise<void> {
        await this.initPromise;
        if (this.bridge && this.bridge.eventUpdated) {
            this.bridge.eventUpdated.connect((eventsJson: string) => {
                try {
                    const events = JSON.parse(eventsJson);
                    callback(events);
                } catch (e) {
                    console.error('Failed to parse events:', e);
                }
            });
        } else {
            // Mock events for browser testing
            console.log('Mock: onEventUpdated subscribed');
        }
    }

    async onUnmanagedProcessDetected(callback: (process: UnmanagedProcess) => void): Promise<void> {
        await this.initPromise;
        if (this.bridge && this.bridge.unmanagedProcessDetected) {
            this.bridge.unmanagedProcessDetected.connect((processJson: string) => {
                try {
                    const process = JSON.parse(processJson);
                    callback(process);
                } catch (e) {
                    console.error('Failed to parse unmanaged process:', e);
                }
            });
        } else {
            console.log('Mock: onUnmanagedProcessDetected subscribed');
        }
    }

    // ==================== Process Management ====================

    async getUnmanagedProcesses(): Promise<UnmanagedProcess[]> {
        await this.initPromise;
        if (this.bridge) {
            try {
                const result = await this.bridge.getUnmanagedProcesses();
                return typeof result === 'string' ? JSON.parse(result) : result;
            } catch (error) {
                console.error('Failed to get unmanaged processes:', error);
            }
        }
        return [];
    }

    async killUnmanagedProcess(pid: number): Promise<boolean> {
        await this.initPromise;
        if (this.bridge) {
            try {
                return await this.bridge.killUnmanagedProcess(pid);
            } catch (error) {
                console.error('Failed to kill process:', error);
            }
        }
        return false;
    }

    // ==================== Window Control ====================

    async startDrag(x: number = 0, y: number = 0): Promise<void> {
        await this.initPromise;
        if (this.bridge && typeof this.bridge.startDrag === 'function') {
            try {
                this.bridge.startDrag(x, y);
            } catch (error) {
                console.warn('startDrag call failed:', error);
            }
        }
    }

    async exitLauncher(): Promise<void> {
        await this.initPromise;
        if (this.bridge) {
            try {
                await this.bridge.exitLauncher();
            } catch (error) {
                console.error('Failed to exit launcher:', error);
            }
        } else {
            console.log('Mock: exit launcher');
        }
    }

    // Fix #2: Add bringGameToFront and closeGame bridge methods
    async bringGameToFront(): Promise<boolean> {
        await this.initPromise;
        if (this.bridge) {
            try {
                return await this.bridge.bringGameToFront();
            } catch (error) {
                console.error('Failed to bring game to front:', error);
            }
        }
        return false;
    }

    async closeGame(): Promise<boolean> {
        await this.initPromise;
        if (this.bridge) {
            try {
                return await this.bridge.closeGame();
            } catch (error) {
                console.error('Failed to close game:', error);
            }
        }
        return false;
    }

    // Fix #6: getEvents method (already exists in Python bridge)
    async getEvents(): Promise<any[]> {
        await this.initPromise;
        if (this.bridge) {
            try {
                const result = await this.bridge.getEvents();
                return typeof result === 'string' ? JSON.parse(result) : result;
            } catch (error) {
                console.error('Failed to get events:', error);
            }
        }
        return [];
    }
}

export const bridge = new BridgeService();
