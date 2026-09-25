/** A typed cache with interfaces, generics, and readonly properties. */
export const MAX_ENTRIES = 128;

export enum CacheState {
  Ready = "ready",
  Full = "full",
}

export interface Entry<T> {
  readonly key: string;
  value: T;
  enabled?: boolean;
}

export type Lookup<T> = { found: true; value: T } | { found: false };

export class Cache<T> {
  private readonly entries = new Map<string, Entry<T>>();

  constructor(public readonly label: string, private capacity = MAX_ENTRIES) {}

  get state(): CacheState {
    return this.entries.size >= this.capacity ? CacheState.Full : CacheState.Ready;
  }

  insert(entry: Entry<T>): boolean {
    if (this.state === CacheState.Full || entry.enabled === false) return false;
    this.entries.set(entry.key, entry);
    return true;
  }

  lookup(key: string): Lookup<T> {
    const entry = this.entries.get(key);
    return entry ? { found: true, value: entry.value } : { found: false };
  }

  async summary(prefix: string = "api"): Promise<string> {
    const pattern = /^api[:\w-]+$/i;
    const keys = [...this.entries.keys()].filter((key) => pattern.test(key));
    return `${prefix}: ${this.label} has ${keys.length} entries`;
  }
}
