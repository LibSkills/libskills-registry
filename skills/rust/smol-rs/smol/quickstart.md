# Quickstart

```cpp
// Basic async executor usage
#include <smol/smol.hpp>
#include <iostream>

int main() {
    smol::runtime rt;
    
    // Spawn a simple task
    rt.spawn([]() {
        std::cout << "Hello from smol!" << std::endl;
    });
    
    rt.run();
    return 0;
}
```

```cpp
// Async I/O with timers
#include <smol/smol.hpp>
#include <smol/timer.hpp>
#include <iostream>

int main() {
    smol::runtime rt;
    
    rt.spawn([]() -> smol::task<void> {
        std::cout << "Waiting 1 second..." << std::endl;
        co_await smol::sleep(std::chrono::seconds(1));
        std::cout << "Done waiting!" << std::endl;
    });
    
    rt.run();
    return 0;
}
```

```cpp
// Networking with TCP
#include <smol/smol.hpp>
#include <smol/net.hpp>
#include <iostream>

int main() {
    smol::runtime rt;
    
    rt.spawn([]() -> smol::task<void> {
        auto listener = smol::TcpListener::bind("127.0.0.1:8080").await();
        auto [stream, addr] = listener.accept().await();
        std::cout << "Accepted connection from " << addr << std::endl;
    });
    
    rt.run();
    return 0;
}
```

```cpp
// Task spawning and joining
#include <smol/smol.hpp>
#include <iostream>

int main() {
    smol::runtime rt;
    
    rt.spawn([]() -> smol::task<void> {
        auto task1 = smol::spawn([]() -> int {
            return 42;
        });
        
        int result = co_await task1;
        std::cout << "Result: " << result << std::endl;
    });
    
    rt.run();
    return 0;
}
```

```cpp
// Channel communication
#include <smol/smol.hpp>
#include <smol/channel.hpp>
#include <iostream>

int main() {
    smol::runtime rt;
    auto [tx, rx] = smol::channel::unbounded<int>();
    
    rt.spawn([tx]() -> smol::task<void> {
        co_await tx.send(100);
    });
    
    rt.spawn([rx]() -> smol::task<void> {
        int value = co_await rx.recv();
        std::cout << "Received: " << value << std::endl;
    });
    
    rt.run();
    return 0;
}
```

```cpp
// File I/O
#include <smol/smol.hpp>
#include <smol/fs.hpp>
#include <iostream>

int main() {
    smol::runtime rt;
    
    rt.spawn([]() -> smol::task<void> {
        auto file = smol::File::open("test.txt").await();
        std::string contents = co_await file.read_to_end();
        std::cout << "File contents: " << contents << std::endl;
    });
    
    rt.run();
    return 0;
}
```