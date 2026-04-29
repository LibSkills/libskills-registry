# Pitfalls

```cpp
// BAD: Forgetting to close handles before loop exit
#include <uv.h>
int main() {
    uv_timer_t timer;
    uv_timer_init(uv_default_loop(), &timer);
    uv_timer_start(&timer, [](uv_timer_t*){}, 1000, 0);
    uv_run(uv_default_loop(), UV_RUN_DEFAULT);
    // timer handle is leaked!
    return 0;
}

// GOOD: Properly closing handles
#include <uv.h>
void on_close(uv_handle_t *handle) {
    delete handle;
}
int main() {
    uv_timer_t *timer = new uv_timer_t;
    uv_timer_init(uv_default_loop(), timer);
    uv_timer_start(timer, [](uv_timer_t *t){
        uv_close((uv_handle_t*)t, on_close);
    }, 1000, 0);
    uv_run(uv_default_loop(), UV_RUN_DEFAULT);
    return 0;
}
```

```cpp
// BAD: Using stack-allocated handles with async operations
#include <uv.h>
void bad_timer() {
    uv_timer_t timer;
    uv_timer_init(uv_default_loop(), &timer);
    uv_timer_start(&timer, [](uv_timer_t*){}, 1000, 0);
    // timer goes out of scope, but loop still references it!
}

// GOOD: Heap-allocating handles with proper cleanup
#include <uv.h>
void good_timer() {
    uv_timer_t *timer = new uv_timer_t;
    uv_timer_init(uv_default_loop(), timer);
    uv_timer_start(timer, [](uv_timer_t *t){
        uv_close((uv_handle_t*)t, [](uv_handle_t *h){
            delete h;
        });
    }, 1000, 0);
}
```

```cpp
// BAD: Ignoring error return values
#include <uv.h>
int main() {
    uv_tcp_t server;
    uv_tcp_init(uv_default_loop(), &server);
    struct sockaddr_in addr;
    uv_ip4_addr("0.0.0.0", 8080, &addr);
    uv_tcp_bind(&server, (const struct sockaddr*)&addr, 0);
    uv_listen((uv_stream_t*)&server, 128, nullptr); // ignored return value!
    uv_run(uv_default_loop(), UV_RUN_DEFAULT);
    return 0;
}

// GOOD: Always check return values
#include <uv.h>
#include <iostream>
int main() {
    uv_tcp_t server;
    uv_tcp_init(uv_default_loop(), &server);
    struct sockaddr_in addr;
    int r = uv_ip4_addr("0.0.0.0", 8080, &addr);
    if (r) { std::cerr << "IP error: " << uv_strerror(r) << std::endl; return 1; }
    r = uv_tcp_bind(&server, (const struct sockaddr*)&addr, 0);
    if (r) { std::cerr << "Bind error: " << uv_strerror(r) << std::endl; return 1; }
    r = uv_listen((uv_stream_t*)&server, 128, nullptr);
    if (r) { std::cerr << "Listen error: " << uv_strerror(r) << std::endl; return 1; }
    uv_run(uv_default_loop(), UV_RUN_DEFAULT);
    return 0;
}
```

```cpp
// BAD: Calling uv_run multiple times recursively
#include <uv.h>
void recursive_cb(uv_timer_t *handle) {
    uv_run(uv_default_loop(), UV_RUN_NOWAIT); // recursive call!
}

// GOOD: Use uv_stop to exit loop, then restart
#include <uv.h>
void proper_cb(uv_timer_t *handle) {
    uv_stop(uv_default_loop());
    // Do work, then call uv_run again if needed
}
```

```cpp
// BAD: Modifying handle state without stopping it first
#include <uv.h>
int main() {
    uv_timer_t timer;
    uv_timer_init(uv_default_loop(), &timer);
    uv_timer_start(&timer, [](uv_timer_t*){}, 1000, 500);
    uv_timer_set_repeat(&timer, 200); // should stop first!
    uv_run(uv_default_loop(), UV_RUN_DEFAULT);
    return 0;
}

// GOOD: Stop before modification
#include <uv.h>
int main() {
    uv_timer_t timer;
    uv_timer_init(uv_default_loop(), &timer);
    uv_timer_start(&timer, [](uv_timer_t*){}, 1000, 500);
    uv_timer_stop(&timer);
    uv_timer_set_repeat(&timer, 200);
    uv_timer_start(&timer, [](uv_timer_t*){}, 0, 200);
    uv_run(uv_default_loop(), UV_RUN_DEFAULT);
    return 0;
}
```

```cpp
// BAD: Using uv_fs_req_cleanup on stack-allocated request while still in use
#include <uv.h>
void cb(uv_fs_t *req) {
    // req might be stack-allocated!
    uv_fs_req_cleanup(req);
}

// GOOD: Only cleanup heap-allocated requests after callback completes
#include <uv.h>
void cb(uv_fs_t *req) {
    // Process result
    uv_fs_req_cleanup(req);
    delete req;
}
```