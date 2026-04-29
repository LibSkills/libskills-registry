# Pitfalls

```cpp
// BAD: Blocking the executor thread
#include <smol/smol.hpp>
#include <thread>
#include <iostream>

int main() {
    smol::runtime rt;
    
    rt.spawn([]() {
        std::this_thread::sleep_for(std::chrono::seconds(5)); // Blocks executor!
        std::cout << "Done sleeping" << std::endl;
    });
    
    rt.run(); // Won't process other tasks for 5 seconds
    return 0;
}
```

```cpp
// GOOD: Using async sleep
#include <smol/smol.hpp>
#include <smol/timer.hpp>
#include <iostream>

int main() {
    smol::runtime rt;
    
    rt.spawn([]() -> smol::task<void> {
        co_await smol::sleep(std::chrono::seconds(5)); // Non-blocking
        std::cout << "Done sleeping" << std::endl;
    });
    
    rt.run(); // Processes other tasks during sleep
    return 0;
}
```

```cpp
// BAD: Forgetting to co_await
#include <smol/smol.hpp>
#include <smol/timer.hpp>
#include <iostream>

int main() {
    smol::runtime rt;
    
    rt.spawn([]() -> smol::task<void> {
        smol::sleep(std::chrono::seconds(1)); // Missing co_await!
        std::cout << "This runs immediately" << std::endl;
    });
    
    rt.run();
    return 0;
}
```

```cpp
// GOOD: Properly awaiting async operations
#include <smol/smol.hpp>
#include <smol/timer.hpp>
#include <iostream>

int main() {
    smol::runtime rt;
    
    rt.spawn([]() -> smol::task<void> {
        co_await smol::sleep(std::chrono::seconds(1)); // Proper await
        std::cout << "This runs after 1 second" << std::endl;
    });
    
    rt.run();
    return 0;
}
```

```cpp
// BAD: Mixing blocking I/O with async
#include <smol/smol.hpp>
#include <fstream>
#include <iostream>

int main() {
    smol::runtime rt;
    
    rt.spawn([]() {
        std::ifstream file("data.txt"); // Blocking I/O
        std::string line;
        std::getline(file, line);
        std::cout << line << std::endl;
    });
    
    rt.run();
    return 0;
}
```

```cpp
// GOOD: Using async file I/O
#include <smol/smol.hpp>
#include <smol/fs.hpp>
#include <iostream>

int main() {
    smol::runtime rt;
    
    rt.spawn([]() -> smol::task<void> {
        auto file = smol::File::open("data.txt").await();
        std::string contents = co_await file.read_to_end();
        std::cout << contents << std::endl;
    });
    
    rt.run();
    return 0;
}
```