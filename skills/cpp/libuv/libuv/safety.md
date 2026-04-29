# Safety

**Red Line 1: Never call uv_run from within a callback (recursive event loop)**

```cpp
// BAD: Recursive event loop call
void timer_cb(uv_timer_t *handle) {
    uv_run(uv_default_loop(), UV_RUN_DEFAULT); // CRASH or undefined behavior
}

// GOOD: Use uv_stop to exit and re-enter
void timer_cb(uv_timer_t *handle) {
    uv_stop(uv_default_loop());
    // Process results after uv_run returns
}
```

**Red Line 2: Never access a handle after calling uv_close on it**

```cpp
// BAD: Using handle after close
void close_cb(uv_handle_t *handle) {
    uv_timer_t *timer = (uv_timer_t*)handle;
    uv_timer_start(timer, nullptr, 0, 0); // Undefined behavior!
}

// GOOD: Handle is invalid after close
void close_cb(uv_handle_t *handle) {
    // Only cleanup, no operations on handle
    delete handle;
}
```

**Red Line 3: Never call uv_fs_req_cleanup on a request that is still in flight**

```cpp
// BAD: Cleaning up while operation is pending
uv_fs_t req;
uv_fs_open(uv_default_loop(), &req, "file.txt", O_RDONLY, 0, nullptr);
uv_fs_req_cleanup(&req); // Undefined behavior!

// GOOD: Only cleanup after callback
void open_cb(uv_fs_t *req) {
    uv_fs_req_cleanup(req);
}
```

**Red Line 4: Never use stack-allocated handles with async operations that outlive the scope**

```cpp
// BAD: Stack handle with async operation
void setup_timer() {
    uv_timer_t timer;
    uv_timer_init(uv_default_loop(), &timer);
    uv_timer_start(&timer, timer_cb, 1000, 0);
    // timer destroyed when function returns, but loop still references it!
}

// GOOD: Heap-allocate and manage lifetime
void setup_timer() {
    uv_timer_t *timer = new uv_timer_t;
    uv_timer_init(uv_default_loop(), timer);
    uv_timer_start(timer, timer_cb, 1000, 0);
}
```

**Red Line 5: Never ignore error return values from libuv functions**

```cpp
// BAD: Ignoring errors
uv_tcp_bind(&server, (const struct sockaddr*)&addr, 0); // Might fail silently

// GOOD: Always check and handle errors
int r = uv_tcp_bind(&server, (const struct sockaddr*)&addr, 0);
if (r < 0) {
    // Handle error appropriately
    std::cerr << "Bind failed: " << uv_strerror(r) << std::endl;
    uv_close((uv_handle_t*)&server, nullptr);
    return;
}
```