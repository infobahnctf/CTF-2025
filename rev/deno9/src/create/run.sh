cp main_real.ts main_fake.ts
sed -i -E 's/v0.../v9999/g' main_fake.ts
sed -i -E 's/[0-9]/9/g' main_fake.ts
sed -i -E 's/\*/\+/g' main_fake.ts
sed -i -E 's/\-/\+/g' main_fake.ts

docker build -t dedenono . -f Dockerfile1
docker run --rm --name dedenono-container1 dedenono &
sleep 3
docker cp dedenono-container1:/deno-dir/v8_code_cache_v2 ./v8_code_cache_v2-1
docker cp dedenono-container1:/deno-dir/v8_code_cache_v2-wal ./v8_code_cache_v2-1-wal
docker cp dedenono-container1:/deno-dir/v8_code_cache_v2-shm ./v8_code_cache_v2-1-shm
docker container stop dedenono-container1

docker build -t dedenono . -f Dockerfile2
docker run --rm --name dedenono-container2 dedenono &
sleep 3
docker cp dedenono-container2:/deno-dir/v8_code_cache_v2 ./v8_code_cache_v2-2
docker cp dedenono-container2:/deno-dir/v8_code_cache_v2-wal ./v8_code_cache_v2-2-wal
docker cp dedenono-container2:/deno-dir/v8_code_cache_v2-shm ./v8_code_cache_v2-2-shm
docker container stop dedenono-container2

sqlite3 v8_code_cache_v2-2 "UPDATE codecache SET source_hash=$(sqlite3 v8_code_cache_v2-1 'SELECT source_hash FROM codecache;')"

cp v8_code_cache_v2-2 ../attachment/v8_code_cache_v2
cp main_fake.ts ../attachment/main.ts