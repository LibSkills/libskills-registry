# Threading

```cpp
// Thread safety: Cobra is NOT thread-safe
#include <cobra/cobra.hpp>
#include <iostream>
#include <thread>

// BAD: Concurrent access to command hierarchy
int main() {
    cobra::Command root;
    root.Use("app");
    
    std::thread t1([&root]() {
        root.AddCommand("cmd1");  // Thread 1 modifies
    });
    
    std::thread t2([&root]() {
        root.AddCommand("cmd2");  // Thread 2 modifies concurrently
    });
    
    t1.join();
    t2.join();
    
    root.Execute();
    return 0;
}

// GOOD: Build hierarchy in single thread
#include <cobra/cobra.hpp>
#include <iostream>

int main() {
    cobra::Command root;
    root.Use("app");
    
    // All modifications in main thread
    root.AddCommand("cmd1");
    root.AddCommand("cmd2");
    
    root.Execute();
    return 0;
}
```

```cpp
// Thread safety: Run callbacks
#include <cobra/cobra.hpp>
#include <iostream>
#include <thread>
#include <mutex>

int main() {
    cobra::Command root;
    root.Use("app");
    
    std::mutex mtx;
    int counter = 0;
    
    root.Run([&mtx, &counter](const cobra::Command& cmd, const std::vector<std::string>& args) {
        // Run callback is called once, but if you spawn threads:
        std::thread worker([&mtx, &counter]() {
            std::lock_guard<std::mutex> lock(mtx);
            counter++;
        });
        worker.join();
        
        std::cout << "Counter: " << counter << "\n";
    });
    
    root.Execute();
    return 0;
}
```

```cpp
// Thread safety: Flag access in callbacks
#include <cobra/cobra.hpp>
#include <iostream>
#include <thread>

int main() {
    cobra::Command root;
    root.Use("app");
    
    root.Flags().String("name", "n", "", "Name");
    
    root.Run([](const cobra::Command& cmd, const std::vector<std::string>& args) {
        // Flag access is safe in Run callback (single-threaded context)
        std::string name = cmd.Flags().GetString("name");
        
        // But if you pass cmd to another thread:
        std::thread worker([&cmd]() {
            // UNSAFE: Concurrent flag access
            std::string name = cmd.Flags().GetString("name");
        });
        worker.detach();  // Dangerous
        
        std::cout << "Name: " << name << "\n";
    });
    
    root.Execute();
    return 0;
}
```

```cpp
// Thread safety: Copy flags before threading
#include <cobra/cobra.hpp>
#include <iostream>
#include <thread>
#include <string>

int main() {
    cobra::Command root;
    root.Use("app");
    
    root.Flags().String("name", "n", "", "Name");
    root.Flags().Int("count", "c", 1, "Count");
    
    root.Run([](const cobra::Command& cmd, const std::vector<std::string>& args) {
        // Copy flag values before threading
        std::string name = cmd.Flags().GetString("name");
        int count = cmd.Flags().GetInt("count");
        
        // Now safe to use in threads
        std::thread worker([name, count]() {
            std::cout << "Name: " << name << ", Count: " << count << "\n";
        });
        worker.join();
    });
    
    root.Execute();
    return 0;
}
```