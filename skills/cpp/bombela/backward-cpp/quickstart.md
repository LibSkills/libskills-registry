# Quickstart


```cpp
// Pattern 1: Minimal setup with signal handling
#include "backward.hpp"

int main() {
    backward::SignalHandling sh;  // Auto-print stack traces on crash
    // Your code here
    return 0;
}
```

```cpp
// Pattern 2: Manual stack trace printing
#include "backward.hpp"
#include <iostream>

void print_trace() {
    using namespace backward;
    StackTrace st;
    st.load_here(32);  // Capture up to 32 frames
    Printer p;
    p.print(st);
}

int main() {
    print_trace();
    return 0;
}
```

```cpp
// Pattern 3: Custom trace with source snippets
#include "backward.hpp"
#include <iostream>

int main() {
    backward::StackTrace st;
    st.load_here(32);
    
    backward::Printer p;
    p.snippet = true;       // Show source code snippets
    p.color_mode = backward::ColorMode::always;
    p.address = true;       // Show memory addresses
    p.print(st);
    return 0;
}
```

```cpp
// Pattern 4: Trace from a specific thread
#include "backward.hpp"
#include <thread>

void worker() {
    backward::StackTrace st;
    st.load_here(32);
    backward::Printer().print(st);
}

int main() {
    std::thread t(worker);
    t.join();
    return 0;
}
```

```cpp
// Pattern 5: Resolving trace with object files
#include "backward.hpp"
#include <iostream>

int main() {
    backward::StackTrace st;
    st.load_here(32);
    
    backward::TraceResolver tr;
    tr.load_stacktrace(st);
    
    for (size_t i = 0; i < st.size(); ++i) {
        backward::ResolvedTrace trace = tr.resolve(st[i]);
        std::cout << "#" << i << " " 
                  << trace.object_filename << " "
                  << trace.object_function << "\n";
    }
    return 0;
}
```

```cpp
// Pattern 6: Signal handling with custom behavior
#include "backward.hpp"
#include <iostream>
#include <signal.h>

int main() {
    backward::SignalHandling sh;
    
    // Trigger a segfault to test
    // int* p = nullptr;
    // *p = 42;  // Will print stack trace
    
    std::cout << "Backward-cpp signal handlers installed\n";
    return 0;
}
```