/**
 * In-memory per-gatewayId rate safety (LINK transport boundary only).
 * Drops excess events — no retry, no business logic.
 */

export const DEFAULT_GATEWAY_MAX_EVENTS_PER_SECOND = 1_000;

export interface GatewayRateThrottleOptions {
  readonly maxEventsPerSecond?: number;
  readonly now?: () => number;
}

interface ThrottleWindow {
  windowStartMs: number;
  count: number;
}

export class GatewayRateThrottle {
  private readonly windows = new Map<string, ThrottleWindow>();
  private readonly maxEventsPerSecond: number;
  private readonly now: () => number;

  public constructor(options: GatewayRateThrottleOptions = {}) {
    this.maxEventsPerSecond = options.maxEventsPerSecond ?? DEFAULT_GATEWAY_MAX_EVENTS_PER_SECOND;
    this.now = options.now ?? Date.now;
  }

  /** Returns true when the event may proceed; false when rate limit exceeded (drop). */
  public allow(gatewayId: string): boolean {
    const normalized = gatewayId.trim();
    if (!normalized) {
      return false;
    }

    const nowMs = this.now();
    const windowStartMs = Math.floor(nowMs / 1000) * 1000;
    const existing = this.windows.get(normalized);

    if (existing === undefined || existing.windowStartMs !== windowStartMs) {
      this.windows.set(normalized, { windowStartMs, count: 1 });
      return true;
    }

    if (existing.count >= this.maxEventsPerSecond) {
      return false;
    }

    existing.count += 1;
    return true;
  }

  public reset(): void {
    this.windows.clear();
  }
}
