# Quickstart

```cpp
#include <uv.h>
#include <iostream>
#include <cstring>

// 1. Initialize a default loop
int main() {
    uv_loop_t *loop = uv_default_loop();
    std::cout << "Loop initialized" << std::endl;
    uv_run(loop, UV_RUN_DEFAULT);
    uv_loop_close(loop);
    return 0;
}
```

```cpp
// 2. Create a TCP server
#include <uv.h>
#include <iostream>

void on_connection(uv_stream_t *server, int status) {
    if (status < 0) {
        std::cerr << "Connection error: " << uv_strerror(status) << std::endl;
        return;
    }
    uv_tcp_t *client = new uv_tcp_t;
    uv_tcp_init(uv_default_loop(), client);
    if (uv_accept(server, (uv_stream_t*)client) == 0) {
        std::cout << "Client connected" << std::endl;
    } else {
        delete client;
    }
}

int main() {
    uv_tcp_t server;
    uv_tcp_init(uv_default_loop(), &server);
    
    struct sockaddr_in addr;
    uv_ip4_addr("0.0.0.0", 8080, &addr);
    uv_tcp_bind(&server, (const struct sockaddr*)&addr, 0);
    
    int r = uv_listen((uv_stream_t*)&server, 128, on_connection);
    if (r) {
        std::cerr << "Listen error: " << uv_strerror(r) << std::endl;
        return 1;
    }
    
    uv_run(uv_default_loop(), UV_RUN_DEFAULT);
    return 0;
}
```

```cpp
// 3. Timer example
#include <uv.h>
#include <iostream>

void timer_cb(uv_timer_t *handle) {
    static int count = 0;
    std::cout << "Timer tick " << ++count << std::endl;
    if (count >= 5) {
        uv_timer_stop(handle);
        uv_close((uv_handle_t*)handle, nullptr);
    }
}

int main() {
    uv_timer_t timer;
    uv_timer_init(uv_default_loop(), &timer);
    uv_timer_start(&timer, timer_cb, 1000, 500); // 1s delay, 500ms interval
    
    uv_run(uv_default_loop(), UV_RUN_DEFAULT);
    return 0;
}
```

```cpp
// 4. File I/O with async operations
#include <uv.h>
#include <iostream>
#include <cstring>

void read_cb(uv_fs_t *req) {
    if (req->result < 0) {
        std::cerr << "Read error: " << uv_strerror(req->result) << std::endl;
    } else if (req->result > 0) {
        std::cout.write(static_cast<char*>(req->data), req->result);
    }
    uv_fs_req_cleanup(req);
    delete req;
}

void open_cb(uv_fs_t *req) {
    if (req->result < 0) {
        std::cerr << "Open error: " << uv_strerror(req->result) << std::endl;
        delete req;
        return;
    }
    
    uv_fs_t *read_req = new uv_fs_t;
    char *buf = new char[1024];
    read_req->data = buf;
    
    uv_buf_t iov = uv_buf_init(buf, 1024);
    uv_fs_read(uv_default_loop(), read_req, req->result, &iov, 1, 0, read_cb);
    uv_fs_req_cleanup(req);
    delete req;
}

int main() {
    uv_fs_t *open_req = new uv_fs_t;
    uv_fs_open(uv_default_loop(), open_req, "test.txt", O_RDONLY, 0, open_cb);
    uv_run(uv_default_loop(), UV_RUN_DEFAULT);
    return 0;
}
```

```cpp
// 5. DNS resolution
#include <uv.h>
#include <iostream>
#include <cstring>

void resolve_cb(uv_getaddrinfo_t *resolver, int status, struct addrinfo *res) {
    if (status < 0) {
        std::cerr << "DNS error: " << uv_strerror(status) << std::endl;
        return;
    }
    
    char addr[17] = {0};
    uv_ip4_name((struct sockaddr_in*)res->ai_addr, addr, 16);
    std::cout << "Resolved: " << addr << std::endl;
    
    uv_freeaddrinfo(res);
    delete resolver;
}

int main() {
    uv_getaddrinfo_t *resolver = new uv_getaddrinfo_t;
    struct addrinfo hints;
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = PF_INET;
    hints.ai_socktype = SOCK_STREAM;
    
    uv_getaddrinfo(uv_default_loop(), resolver, resolve_cb, "example.com", "80", &hints);
    uv_run(uv_default_loop(), UV_RUN_DEFAULT);
    return 0;
}
```

```cpp
// 6. Idle handle for background tasks
#include <uv.h>
#include <iostream>

void idle_cb(uv_idle_t *handle) {
    static int count = 0;
    std::cout << "Idle callback " << ++count << std::endl;
    if (count >= 3) {
        uv_idle_stop(handle);
        uv_close((uv_handle_t*)handle, nullptr);
    }
}

int main() {
    uv_idle_t idle;
    uv_idle_init(uv_default_loop(), &idle);
    uv_idle_start(&idle, idle_cb);
    
    uv_run(uv_default_loop(), UV_RUN_DEFAULT);
    return 0;
}
```

```cpp
// 7. Signal handling
#include <uv.h>
#include <iostream>

void signal_cb(uv_signal_t *handle, int signum) {
    std::cout << "Received signal " << signum << std::endl;
    uv_signal_stop(handle);
    uv_close((uv_handle_t*)handle, nullptr);
}

int main() {
    uv_signal_t sig;
    uv_signal_init(uv_default_loop(), &sig);
    uv_signal_start(&sig, signal_cb, SIGINT);
    
    std::cout << "Press Ctrl+C to trigger signal" << std::endl;
    uv_run(uv_default_loop(), UV_RUN_DEFAULT);
    return 0;
}
```

```cpp
// 8. Pipe communication
#include <uv.h>
#include <iostream>
#include <cstring>

void alloc_buffer(uv_handle_t *handle, size_t suggested_size, uv_buf_t *buf) {
    buf->base = new char[suggested_size];
    buf->len = suggested_size;
}

void read_cb(uv_stream_t *stream, ssize_t nread, const uv_buf_t *buf) {
    if (nread < 0) {
        if (nread != UV_EOF) {
            std::cerr << "Read error: " << uv_strerror(nread) << std::endl;
        }
        uv_close((uv_handle_t*)stream, nullptr);
    } else if (nread > 0) {
        std::cout.write(buf->base, nread);
    }
    delete[] buf->base;
}

int main() {
    uv_pipe_t pipe;
    uv_pipe_init(uv_default_loop(), &pipe, 0);
    uv_pipe_open(&pipe, 0); // stdin
    
    uv_read_start((uv_stream_t*)&pipe, alloc_buffer, read_cb);
    uv_run(uv_default_loop(), UV_RUN_DEFAULT);
    return 0;
}
```