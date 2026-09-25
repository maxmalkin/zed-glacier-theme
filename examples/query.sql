-- Fields, aliases, functions, and literals.
SELECT service.name, COUNT(*) AS entry_count
FROM service
JOIN entry ON entry.service_id = service.id
WHERE entry.enabled = TRUE AND entry.created_at >= '2026-01-01'
GROUP BY service.name
HAVING COUNT(*) < 128
ORDER BY entry_count DESC;
