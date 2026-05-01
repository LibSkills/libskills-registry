# Performance

**Event Loop Performance**

The Nana event loop (`nana::exec()`) is single-threaded and processes events sequentially. Long-running operations in event handlers will block the UI.

```cpp
#include <nana/gui.hpp>
#include <nana/gui/widgets/button.hpp>
#include <nana/gui/widgets/label.hpp>
#include <thread>
#include <atomic>

// BAD: Blocking the event loop
void bad_blocking() {
    nana::form fm;
    nana::button btn(fm, nana::rectangle(10, 10, 100, 30));
    btn.caption("Process");
    
    btn.events().click([]() {
        // This blocks the UI for 5 seconds
        std::this_thread::sleep_for(std::chrono::seconds(5));
    });
    
    fm.show();
    nana::exec();
}

// GOOD: Using timer for non-blocking operation
void good_non_blocking() {
    nana::form fm;
    nana::button btn(fm, nana::rectangle(10, 10, 100, 30));
    nana::label status(fm, nana::rectangle(10, 50, 200, 30));
    btn.caption("Start");
    status.caption("Idle");
    
    std::atomic<bool> processing{false};
    nana::timer tmr;
    
    btn.events().click([&processing, &tmr]() {
        if (!processing) {
            processing = true;
            tmr.start();
        }
    });
    
    tmr.elapse([&processing, &status, &tmr, count = 0]() mutable {
        if (++count >= 50) { // 5 seconds at 100ms intervals
            tmr.stop();
            processing = false;
            count = 0;
            status.caption("Done!");
        } else {
            status.caption("Processing: " + std::to_string(count * 100) + "ms");
        }
    });
    tmr.interval(std::chrono::milliseconds(100));
    
    fm.show();
    nana::exec();
}
```

**Drawing Performance**

Custom drawing operations should be efficient. Use `nana::drawing` for event-driven rendering and avoid redrawing the entire widget unnecessarily.

```cpp
#include <nana/gui.hpp>
#include <nana/gui/drawing.hpp>
#include <nana/gui/widgets/label.hpp>
#include <vector>

// Efficient drawing with caching
class EfficientDrawer {
    nana::form fm;
    nana::drawing dw;
    nana::paint::graphics cached_bg;
    bool needs_redraw = true;
    
public:
    EfficientDrawer()
        : fm(nana::size(500, 400))
        , dw(fm)
        , cached_bg(fm.size())
    {
        fm.caption("Efficient Drawing");
        
        // Only redraw when needed
        dw.draw([this](nana::paint::graphics& g) {
            if (needs_redraw) {
                render_background();
                needs_redraw = false;
            }
            // Blit cached background
            g.bitblit(nana::rectangle(fm.size()), cached_bg, nana::point(0, 0));
        });
        
        fm.show();
    }
    
    void invalidate() {
        needs_redraw = true;
        dw.update(); // Trigger redraw
    }
    
private:
    void render_background() {
        cached_bg.rectangle(true, nana::colors::white);
        // Draw complex shapes only once
        for (int i = 0; i < 100; ++i) {
            cached_bg.line(
                {rand() % 500, rand() % 400},
                {rand() % 500, rand() % 400},
                nana::colors::gray
            );
        }
    }
    
    void run() { nana::exec(); }
};
```

**Memory Allocation Patterns**

Nana allocates memory for widgets and graphics objects. Minimize allocations in performance-critical paths.

```cpp
#include <nana/gui.hpp>
#include <nana/gui/widgets/label.hpp>
#include <nana/gui/timer.hpp>
#include <string>
#include <sstream>

// BAD: Frequent string allocations
void bad_string_allocation() {
    nana::form fm;
    nana::label lbl(fm, nana::rectangle(10, 10, 200, 30));
    
    nana::timer tmr;
    tmr.elapse([&lbl, count = 0]() mutable {
        // Creates new string every tick
        lbl.caption("Count: " + std::to_string(count++));
    });
    tmr.interval(std::chrono::milliseconds(100));
    tmr.start();
    
    fm.show();
    nana::exec();
}

// GOOD: Pre-allocate and reuse string buffer
void good_string_reuse() {
    nana::form fm;
    nana::label lbl(fm, nana::rectangle(10, 10, 200, 30));
    std::string buffer;
    buffer.reserve(32); // Pre-allocate
    
    nana::timer tmr;
    tmr.elapse([&lbl, &buffer, count = 0]() mutable {
        buffer = "Count: ";
        buffer += std::to_string(count++);
        lbl.caption(buffer);
    });
    tmr.interval(std::chrono::milliseconds(100));
    tmr.start();
    
    fm.show();
    nana::exec();
}
```

**Layout Performance**

Complex layouts with many widgets can impact performance. Use efficient layout strategies.

```cpp
#include <nana/gui.hpp>
#include <nana/gui/place.hpp>
#include <nana/gui/widgets/button.hpp>
#include <vector>

// Efficient layout with minimal widgets
class EfficientLayout {
    nana::form fm;
    nana::place layout;
    std::vector<nana::button> buttons;
    
public:
    EfficientLayout(int num_buttons)
        : fm(nana::size(800, 600))
        , layout(fm)
    {
        fm.caption("Efficient Layout");
        
        // Create layout string once
        std::string div_str = "vert ";
        for (int i = 0; i < num_buttons; ++i) {
            div_str += "<btn" + std::to_string(i) + " weight=30>";
            buttons.emplace_back(fm);
            buttons.back().caption("Button " + std::to_string(i + 1));
        }
        
        layout.div(div_str);
        
        // Assign widgets to fields
        for (int i = 0; i < num_buttons; ++i) {
            layout["btn" + std::to_string(i)] << buttons[i];
        }
        
        layout.collocate(); // Only call once
        fm.show();
    }
    
    void run() { nana::exec(); }
};
```