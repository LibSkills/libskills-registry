# Lifecycle


```cpp
// Construction: StackTrace objects are lightweight
#include "backward.hpp"

void example_construction() {
    // Default construction - empty stack trace
    backward::StackTrace st1;
    
    // Construction with immediate capture
    backward::StackTrace st2;
    st2.load_here(32);  // Captures current stack
    
    // Copy construction (shallow copy of trace data)
    backward::StackTrace st3 = st2;
    
    // Move construction
    backward::StackTrace st4 = std::move(st3);
}
```

```cpp
// Destruction: No special cleanup needed
#include "backward.hpp"
#include <vector>

void example_destruction() {
    {
        backward::StackTrace st;
        st.load_here(32);
        // st destroyed automatically when leaving scope
    }
    
    // Works with containers
    std::vector<backward::StackTrace> traces;
    {
        backward::StackTrace st;
        st.load_here(32);
        traces.push_back(std::move(st));
    }  // st destroyed, but data moved to vector
    
    // Vector manages its own resources
    traces.clear();  // All traces properly cleaned up
}
```

```cpp
// Move semantics: Efficient transfer of trace data
#include "backward.hpp"
#include <vector>

class ErrorReporter {
    backward::StackTrace trace_;
public:
    ErrorReporter() {
        trace_.load_here(32);
    }
    
    // Move constructor
    ErrorReporter(ErrorReporter&& other) noexcept 
        : trace_(std::move(other.trace_)) {}
    
    // Move assignment
    ErrorReporter& operator=(ErrorReporter&& other) noexcept {
        if (this != &other) {
            trace_ = std::move(other.trace_);
        }
        return *this;
    }
    
    void print() const {
        backward::Printer().print(trace_);
    }
};

int main() {
    std::vector<ErrorReporter> reporters;
    reporters.push_back(ErrorReporter());  // Uses move semantics
    reporters[0].print();
    return 0;
}
```

```cpp
// Resource management: Printer and TraceResolver
#include "backward.hpp"
#include <memory>

class TraceManager {
    std::unique_ptr<backward::TraceResolver> resolver_;
public:
    TraceManager() : resolver_(std::make_unique<backward::TraceResolver>()) {}
    
    void capture_and_resolve() {
        backward::StackTrace st;
        st.load_here(32);
        resolver_->load_stacktrace(st);
        
        for (size_t i = 0; i < st.size(); ++i) {
            auto trace = resolver_->resolve(st[i]);
            // Process resolved trace
        }
    }
    
    // Printer is lightweight, can be created on demand
    void print_trace(const backward::StackTrace& st) {
        backward::Printer p;
        p.snippet = true;
        p.print(st);
    }
};
```