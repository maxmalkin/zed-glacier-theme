# Cache service

A **small typed cache** with *predictable behavior* and `MAX_ENTRIES = 128`.

> Comments, documentation, and quoted text should remain easy to read.

- [x] Separate keys from values
- [ ] Review [the API documentation](https://example.com/cache)
- Preserve **bold**, *italic*, and ~~obsolete~~ text

## Rust example

```rust
let mut cache = Cache::new("api");
cache.insert(42)?;
println!("{}", cache.render());
```

## Python example

```python
entry = Entry(key="api:users", value=42)
print(f"{entry.key}: {entry.value}")
```

## TypeScript example

```typescript
const cache = new Cache<number>("api");
cache.insert({ key: "users", value: 42, enabled: true });
```

| Field | Type | Required |
| --- | --- | --- |
| `key` | `string` | Yes |
| `enabled` | `boolean` | No |
