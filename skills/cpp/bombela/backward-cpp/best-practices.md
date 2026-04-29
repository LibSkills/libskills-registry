# Best Practices


```cpp
// Best Practice 1: Use RAII wrapper for safe stack trace capture
#include "backward.hpp"
#include <string>
#include <sstream>

class StackTraceCapture {
    backward::StackTrace st_;
public:
    StackTraceCapture(size_t max_depth = 64) {
        st_.load_here(max_depth);
    }
    
    std::string str() const {
        std::stringstream ss;
        backward::Printer p;
        p.print(st_, ss);
        return ss.str();
    }
    
    void print() const {
        backward::Printer p;
        p.print(st_);
    }
};

void risky_function() {
    StackTraceCapture capture;
    // ... do risky stuff ...
    if (/* error */) {
        capture.print();
    }
}
```

```cpp
// Best Practice 2: Integrate with logging systems
#include "backward.hpp"
#include <iostream>
#include <fstream>

class Logger {
    std::ofstream log_file_;
public:
    Logger(const std::string& path) : log_file_(path) {}
    
    void log_error(const std::string& msg) {
        backward::StackTrace st;
        st.load_here(32);
        
        backward::Printer p;
        p.snippet = true;
        
        log_file_ << "ERROR: " << msg << "\n";
        p.print(st, log_file_);
        log_file_ << "\n";
        log_file_.flush();
    }
};

int main() {
    Logger logger("error.log");
    logger.log_error("Something went wrong");
    return 0;
}
```

```cpp
// Best Practice 3: Conditional compilation for release builds
#include "backward.hpp"

#ifdef BACKWARD_ENABLED
    backward::SignalHandling sh;
#endif

void debug_trace() {
#ifdef BACKWARD_ENABLED
    backward::StackTrace st;
    st.load_here(32);
    backward::Printer().print(st);
#endif
}

int main() {
    debug_trace();
    return 0;
}
```

```cpp
// Best Practice 4: Custom formatter for production traces
#include "backward.hpp"
#include <iostream>
#include <iomanip>

void print_compact_trace() {
    backward::StackTrace st;
    st.load_here(32);
    
    backward::TraceResolver tr;
    tr.load_stacktrace(st);
    
    for (size_t i = 0; i < st.size(); ++i) {
        auto trace = tr.resolve(st[i]);
        std::cout << std::setw(3) << i << ": "
                  << trace.object_function << " ["
                  << trace.source.filename << ":"
                  << trace.source.line << "]\n";
    }
}

int main() {
    print_compact_trace();
    return 0;
}
```