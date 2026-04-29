# Pitfalls


```cpp
// PITFALL 1: Missing debug symbols
// BAD - No debug info, trace shows only addresses
// Compile with: g++ -O2 main.cpp
#include "backward.hpp"
int main() {
    backward::StackTrace st;
    st.load_here(32);
    backward::Printer().print(st);  // Shows ?? instead of function names
    return 0;
}

// GOOD - Compile with debug symbols
// Compile with: g++ -g -O2 main.cpp
#include "backward.hpp"
int main() {
    backward::StackTrace st;
    st.load_here(32);
    backward::Printer().print(st);  // Shows function names and line numbers
    return 0;
}
```

```cpp
// PITFALL 2: Forgetting to link required libraries
// BAD - Missing -ldl and -lbfd
// Compile: g++ -g main.cpp -DBACKWARD_HAS_BFD=1
#include "backward.hpp"
int main() {
    backward::StackTrace st;
    st.load_here(32);
    backward::Printer().print(st);  // Linker errors at compile time
    return 0;
}

// GOOD - Proper linking
// Compile: g++ -g main.cpp -DBACKWARD_HAS_BFD=1 -ldl -lbfd
#include "backward.hpp"
int main() {
    backward::StackTrace st;
    st.load_here(32);
    backward::Printer().print(st);  // Works correctly
    return 0;
}
```

```cpp
// PITFALL 3: Signal handling initialization order with Folly
// BAD - SignalHandling before folly::init
#include "backward.hpp"
#include <folly/init/Init.h>

int main(int argc, char** argv) {
    backward::SignalHandling sh;  // Wrong order!
    folly::init(&argc, &argv);
    return 0;
}

// GOOD - SignalHandling after folly::init
#include "backward.hpp"
#include <folly/init/Init.h>

int main(int argc, char** argv) {
    folly::init(&argc, &argv);
    backward::SignalHandling sh;  // Correct order
    return 0;
}
```

```cpp
// PITFALL 4: Using SignalHandling in shared libraries
// BAD - Multiple SignalHandling instances in different shared objects
// libfoo.so
#include "backward.hpp"
static backward::SignalHandling sh_foo;

// libbar.so
#include "backward.hpp"
static backward::SignalHandling sh_bar;  // Conflict!

// GOOD - Single instance in main executable
// main.cpp
#include "backward.hpp"
backward::SignalHandling sh;  // Only one instance
```

```cpp
// PITFALL 5: Not handling large stack depths
// BAD - Fixed small buffer may miss frames
#include "backward.hpp"
void deep_recursion(int n) {
    backward::StackTrace st;
    st.load_here(5);  // Only captures 5 frames
    if (n > 0) deep_recursion(n - 1);
}

// GOOD - Adequate buffer size
#include "backward.hpp"
void deep_recursion(int n) {
    backward::StackTrace st;
    st.load_here(64);  // Captures up to 64 frames
    if (n > 0) deep_recursion(n - 1);
}
```

```cpp
// PITFALL 6: Assuming thread safety of Printer
// BAD - Concurrent printing from multiple threads
#include "backward.hpp"
#include <thread>

void print_trace() {
    backward::StackTrace st;
    st.load_here(32);
    backward::Printer p;
    p.print(st);  // Not thread-safe!
}

int main() {
    std::thread t1(print_trace);
    std::thread t2(print_trace);
    t1.join(); t2.join();
    return 0;
}

// GOOD - Serialize access
#include "backward.hpp"
#include <thread>
#include <mutex>

std::mutex print_mutex;
void print_trace() {
    backward::StackTrace st;
    st.load_here(32);
    std::lock_guard<std::mutex> lock(print_mutex);
    backward::Printer p;
    p.print(st);
}
```