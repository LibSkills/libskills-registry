# Lifecycle

```cpp
// Construction and initialization
#include <smol/smol.hpp>
#include <iostream>

int main() {
    // Default construction
    smol::runtime rt;
    
    // Runtime starts in idle state
    std::cout << "Runtime created, no tasks pending" << std::endl;
    
    // Add work
    rt.spawn([]() {
        std::cout << "Task executing" << std::endl;
    });
    
    rt.run(); // Process tasks
    return 0;
}
```

```cpp
// Move semantics for tasks
#include <smol/smol.hpp>
#include <smol/timer.hpp>
#include <iostream>

smol::task<int> create_task() {
    co_return 42;
}

int main() {
    smol::runtime rt;
    
    // Task is move-only
    auto task1 = create_task();
    auto task2 = std::move(task1); // OK
    
    // Cannot copy tasks
    // auto task3 = task1; // Compile error
    
    rt.spawn(std::move(task2));
    rt.run();
    return 0;
}
```

```cpp
// Resource cleanup and destruction
#include <smol/smol.hpp>
#include <smol/net.hpp>
#include <iostream>

class Connection {
    smol::TcpStream stream;
public:
    Connection(smol::TcpStream s) : stream(std::move(s)) {
        std::cout << "Connection established" << std::endl;
    }
    
    ~Connection() {
        std::cout << "Connection closed" << std::endl;
        // Stream automatically cleaned up
    }
};

int main() {
    smol::runtime rt;
    
    rt.spawn([]() -> smol::task<void> {
        auto stream = co_await smol::TcpStream::connect("127.0.0.1:8080");
        Connection conn(std::move(stream));
        // Connection destroyed when scope exits
    });
    
    rt.run();
    return 0;
}
```