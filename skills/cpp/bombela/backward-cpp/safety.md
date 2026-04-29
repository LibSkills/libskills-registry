# Safety


```cpp
// RED LINE 1: NEVER use SignalHandling after fork() without re-initialization
// BAD - Child process inherits broken signal handlers
#include "backward.hpp"
#include <unistd.h>

int main() {
    backward::SignalHandling sh;
    pid_t pid = fork();
    if (pid == 0) {
        // Child: signal handlers may be in invalid state
        int* p = nullptr;
        *p = 42;  // Crash may not print trace correctly
    }
    return 0;
}

// GOOD - Re-initialize in child process
#include "backward.hpp"
#include <unistd.h>

int main() {
    backward::SignalHandling sh;
    pid_t pid = fork();
    if (pid == 0) {
        backward::SignalHandling sh_child;  // Re-initialize
        int* p = nullptr;
        *p = 42;  // Trace prints correctly
    }
    return 0;
}
```

```cpp
// RED LINE 2: NEVER call print() from within a signal handler
// BAD - Direct call in signal handler
#include <signal.h>
#include "backward.hpp"

void handler(int) {
    backward::StackTrace st;
    st.load_here(32);
    backward::Printer().print(st);  // Unsafe! May deadlock
}

int main() {
    signal(SIGINT, handler);
    raise(SIGINT);
    return 0;
}

// GOOD - Use SignalHandling which handles this safely
#include "backward.hpp"
int main() {
    backward::SignalHandling sh;  // Safe signal handling
    raise(SIGINT);  // Will print trace safely
    return 0;
}
```

```cpp
// RED LINE 3: NEVER modify Printer settings while another thread is printing
// BAD - Race condition on Printer state
#include "backward.hpp"
#include <thread>

backward::Printer p;

void print_trace() {
    backward::StackTrace st;
    st.load_here(32);
    p.print(st);
}

int main() {
    std::thread t1(print_trace);
    p.snippet = true;  // Race condition!
    std::thread t2(print_trace);
    t1.join(); t2.join();
    return 0;
}

// GOOD - Use separate Printer instances per thread
#include "backward.hpp"
#include <thread>

void print_trace() {
    backward::Printer p;  // Thread-local instance
    p.snippet = true;
    backward::StackTrace st;
    st.load_here(32);
    p.print(st);
}
```

```cpp
// RED LINE 4: NEVER use backward with stripped binaries
// BAD - Stripped binary loses all debug info
// g++ -g -O2 main.cpp && strip main
#include "backward.hpp"
int main() {
    backward::StackTrace st;
    st.load_here(32);
    backward::Printer().print(st);  // Only shows addresses
    return 0;
}

// GOOD - Keep debug symbols or use separate debug info
// g++ -g -O2 main.cpp
#include "backward.hpp"
int main() {
    backward::StackTrace st;
    st.load_here(32);
    backward::Printer().print(st);  // Shows full details
    return 0;
}
```

```cpp
// RED LINE 5: NEVER assume SignalHandling works with custom signal masks
// BAD - Custom signal mask may block backward's handlers
#include "backward.hpp"
#include <signal.h>

int main() {
    sigset_t mask;
    sigemptyset(&mask);
    sigaddset(&mask, SIGSEGV);
    pthread_sigmask(SIG_BLOCK, &mask, nullptr);  // Blocks SIGSEGV
    
    backward::SignalHandling sh;  // May not work correctly
    
    int* p = nullptr;
    *p = 42;  // Signal handler may not fire
    return 0;
}

// GOOD - Unblock signals before installing handlers
#include "backward.hpp"
#include <signal.h>

int main() {
    sigset_t mask;
    sigemptyset(&mask);
    pthread_sigmask(SIG_SETMASK, nullptr, nullptr);  // Reset to default
    
    backward::SignalHandling sh;  // Works correctly
    
    int* p = nullptr;
    *p = 42;  // Signal handler fires and prints trace
    return 0;
}
```