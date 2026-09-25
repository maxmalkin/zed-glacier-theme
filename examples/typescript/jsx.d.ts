// Minimal local JSX types for this visual fixture; no React dependency required.
declare namespace JSX {
  interface Element {}
  interface IntrinsicElements {
    section: Record<string, unknown>;
    h2: Record<string, unknown>;
    span: Record<string, unknown>;
    button: Record<string, unknown>;
  }
}
