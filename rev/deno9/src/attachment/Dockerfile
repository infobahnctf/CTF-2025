FROM denoland/deno:debian-2.5.6

# ENV DENO_LOG=debug

COPY main.ts main.ts
COPY v8_code_cache_v2 /deno-dir/v8_code_cache_v2
CMD ["deno", "main.ts"]