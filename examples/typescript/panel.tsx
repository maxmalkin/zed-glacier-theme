// Component names, intrinsic tags, props, and embedded expressions.
import { CacheState } from "./cache";

interface BadgeProps {
  readonly state: CacheState;
  count: number;
  onRefresh?: () => void;
}

function Badge({ state, count, onRefresh }: BadgeProps) {
  const ready = state === CacheState.Ready;
  return (
    <section className="cache-card" aria-label={`Cache: ${state}`}>
      <h2>Cache status</h2>
      <span data-ready={ready}>{count} entries</span>
      <button disabled={!ready} onClick={onRefresh}>Refresh</button>
    </section>
  );
}

export function Dashboard() {
  return <Badge state={CacheState.Ready} count={42} />;
}
