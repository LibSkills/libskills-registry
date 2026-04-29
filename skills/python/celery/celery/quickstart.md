# Quickstart

```cpp
// Example 1: Creating a simple Celery task
#include <celery/celery.h>
#include <iostream>

celery::Task add(int x, int y) {
    return celery::Task("add", x, y);
}

int main() {
    celery::Celery app("redis://localhost:6379/0");
    auto result = app.send_task(add(4, 5));
    std::cout << "Task sent: " << result.id() << std::endl;
    return 0;
}
```

```cpp
// Example 2: Defining a task with a result
#include <celery/celery.h>
#include <string>

celery::Task greet(const std::string& name) {
    return celery::Task("greet", name);
}

int main() {
    celery::Celery app("amqp://guest:guest@localhost:5672//");
    auto result = app.send_task(greet("Alice"));
    std::cout << "Result: " << result.get() << std::endl;
    return 0;
}
```

```cpp
// Example 3: Using task options
#include <celery/celery.h>

int main() {
    celery::Celery app("redis://localhost:6379/0");
    
    celery::TaskOptions opts;
    opts.countdown = 10; // Delay 10 seconds
    opts.expires = 3600; // Expire after 1 hour
    
    auto task = celery::Task("process_data", "file.txt")
                    .with_options(opts);
    auto result = app.send_task(task);
    return 0;
}
```

```cpp
// Example 4: Chaining tasks
#include <celery/celery.h>

int main() {
    celery::Celery app("redis://localhost:6379/0");
    
    auto chain = celery::Task("fetch_data", "url")
                    .then(celery::Task("process_data"))
                    .then(celery::Task("store_result"));
    
    auto result = app.send_chain(chain);
    return 0;
}
```

```cpp
// Example 5: Handling task results asynchronously
#include <celery/celery.h>
#include <future>

int main() {
    celery::Celery app("redis://localhost:6379/0");
    
    auto future = app.send_task_async(celery::Task("long_task", 100));
    
    // Do other work while task runs
    std::cout << "Task submitted, doing other work..." << std::endl;
    
    auto result = future.get(); // Blocks until complete
    std::cout << "Task completed: " << result << std::endl;
    return 0;
}
```

```cpp
// Example 6: Error handling
#include <celery/celery.h>
#include <iostream>

int main() {
    try {
        celery::Celery app("redis://localhost:6379/0");
        auto result = app.send_task(celery::Task("divide", 10, 0));
        std::cout << result.get() << std::endl;
    } catch (const celery::TaskException& e) {
        std::cerr << "Task failed: " << e.what() << std::endl;
    } catch (const celery::ConnectionException& e) {
        std::cerr << "Connection error: " << e.what() << std::endl;
    }
    return 0;
}
```