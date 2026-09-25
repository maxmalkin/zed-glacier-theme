FROM python:3.13-slim AS runtime
WORKDIR /app
COPY python/cache.py ./cache.py
ENV CACHE_CAPACITY=128
USER 1000:1000
CMD ["python", "-m", "compileall", "-q", "cache.py"]
