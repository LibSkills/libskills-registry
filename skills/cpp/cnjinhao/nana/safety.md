# Safety

**Condition 1: NEVER modify GUI widgets from threads other than the main thread**

BAD:
```cpp
#include <nana/gui.hpp>
#include <thread>
int main() {
    nana::form fm;
    nana::label lbl(fm, nana::rectangle(10, 10, 200, 30));
    
    std::thread worker([&lbl]() {
        // This will cause undefined behavior or crash
        lbl.caption("Thread update");
    });
    worker.join();
    
    fm.show();
    nana::exec();
}
```

GOOD:
```cpp
#include <nana/gui.hpp>
#include <nana/gui/timer.hpp>
#include <atomic>
int main() {
    nana::form fm;
    nana::label lbl(fm, nana::rectangle(10, 10, 200, 30));
    std::atomic<bool> update_needed{false};
    
    // Worker thread updates atomic flag
    std::thread worker([&update_needed]() {
        std::this_thread::sleep_for(std::chrono::seconds(1));
        update_needed = true;
    });
    worker.detach();
    
    // Timer on main thread checks flag
    nana::timer tmr;
    tmr.elapse([&lbl, &update_needed]() {
        if (update_needed) {
            lbl.caption("Safe update from main thread");
            update_needed = false;
        }
    });
    tmr.interval(std::chrono::milliseconds(100));
    tmr.start();
    
    fm.show();
    nana::exec();
}
```

**Condition 2: NEVER destroy a widget while it still has active event handlers**

BAD:
```cpp
#include <nana/gui.hpp>
int main() {
    nana::form fm;
    auto* btn = new nana::button(fm, nana::rectangle(10, 10, 100, 30));
    btn->caption("Delete me");
    
    btn->events().click([btn]() {
        delete btn; // Dangerous: event handler still active
    });
    
    fm.show();
    nana::exec();
}
```

GOOD:
```cpp
#include <nana/gui.hpp>
#include <memory>
int main() {
    nana::form fm;
    auto btn = std::make_shared<nana::button>(fm, nana::rectangle(10, 10, 100, 30));
    btn->caption("Safe delete");
    
    std::weak_ptr<nana::button> weak_btn = btn;
    btn->events().click([weak_btn, &fm]() {
        if (auto sp = weak_btn.lock()) {
            sp->close(); // Properly close widget
        }
    });
    
    fm.show();
    nana::exec();
}
```

**Condition 3: NEVER call `nana::exec()` recursively or from within an event handler**

BAD:
```cpp
#include <nana/gui.hpp>
int main() {
    nana::form fm;
    nana::button btn(fm, nana::rectangle(10, 10, 100, 30));
    btn.caption("Nested exec");
    
    btn.events().click([]() {
        nana::exec(); // Will cause deadlock or crash
    });
    
    fm.show();
    nana::exec();
}
```

GOOD:
```cpp
#include <nana/gui.hpp>
int main() {
    nana::form fm;
    nana::button btn(fm, nana::rectangle(10, 10, 100, 30));
    btn.caption("Close");
    
    btn.events().click([&fm]() {
        fm.close(); // Proper way to exit
    });
    
    fm.show();
    nana::exec();
}
```

**Condition 4: NEVER access a widget after its parent form has been destroyed**

BAD:
```cpp
#include <nana/gui.hpp>
int main() {
    nana::button* btn = nullptr;
    {
        nana::form fm;
        btn = new nana::button(fm, nana::rectangle(10, 10, 100, 30));
        btn->caption("Temporary");
        fm.show();
        nana::exec(); // Form destroyed when exec returns
    }
    // btn is now dangling - parent form destroyed
    btn->caption("Dangling access"); // Undefined behavior
    delete btn;
}
```

GOOD:
```cpp
#include <nana/gui.hpp>
int main() {
    nana::form fm;
    nana::button btn(fm, nana::rectangle(10, 10, 100, 30));
    btn.caption("Proper lifetime");
    
    fm.show();
    nana::exec();
    // btn is destroyed when fm goes out of scope
}
```

**Condition 5: NEVER use `nana::internal_scope_guard` incorrectly or omit it when accessing shared data from multiple threads**

BAD:
```cpp
#include <nana/gui.hpp>
#include <thread>
#include <vector>
int main() {
    nana::form fm;
    std::vector<int> shared_data;
    
    std::thread writer([&shared_data]() {
        // No protection for shared_data
        shared_data.push_back(42);
    });
    
    std::thread reader([&shared_data]() {
        // No protection for shared_data
        if (!shared_data.empty()) {
            int val = shared_data[0]; // Race condition
        }
    });
    
    writer.join();
    reader.join();
    
    fm.show();
    nana::exec();
}
```

GOOD:
```cpp
#include <nana/gui.hpp>
#include <thread>
#include <vector>
#include <mutex>
int main() {
    nana::form fm;
    std::vector<int> shared_data;
    std::mutex mtx;
    
    std::thread writer([&shared_data, &mtx]() {
        std::lock_guard<std::mutex> lock(mtx);
        shared_data.push_back(42);
    });
    
    std::thread reader([&shared_data, &mtx]() {
        std::lock_guard<std::mutex> lock(mtx);
        if (!shared_data.empty()) {
            int val = shared_data[0]; // Safe access
        }
    });
    
    writer.join();
    reader.join();
    
    fm.show();
    nana::exec();
}
```