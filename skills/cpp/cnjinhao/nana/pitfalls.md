# Pitfalls

**Pitfall 1: Forgetting to call `nana::exec()`**

BAD:
```cpp
#include <nana/gui.hpp>
int main() {
    nana::form fm;
    fm.show();
    // Missing exec() - program exits immediately
    return 0;
}
```

GOOD:
```cpp
#include <nana/gui.hpp>
int main() {
    nana::form fm;
    fm.show();
    nana::exec(); // Starts the event loop
    return 0;
}
```

**Pitfall 2: Modifying widgets from non-main threads**

BAD:
```cpp
#include <nana/gui.hpp>
#include <thread>
int main() {
    nana::form fm;
    nana::label lbl(fm, nana::rectangle(10, 10, 100, 30));
    
    std::thread t([&lbl]() {
        lbl.caption("Updated from thread"); // CRASH - not thread safe
    });
    t.detach();
    
    fm.show();
    nana::exec();
}
```

GOOD:
```cpp
#include <nana/gui.hpp>
#include <nana/gui/timer.hpp>
int main() {
    nana::form fm;
    nana::label lbl(fm, nana::rectangle(10, 10, 100, 30));
    
    nana::timer tmr;
    tmr.elapse([&lbl]() {
        lbl.caption("Updated safely via timer");
    });
    tmr.interval(std::chrono::milliseconds(100));
    tmr.start();
    
    fm.show();
    nana::exec();
}
```

**Pitfall 3: Using dangling references in event handlers**

BAD:
```cpp
#include <nana/gui.hpp>
nana::button* create_button(nana::form& fm) {
    nana::button* btn = new nana::button(fm, nana::rectangle(10, 10, 100, 30));
    btn->events().click([btn]() { // Captures raw pointer
        delete btn; // Deletes button while event system still references it
    });
    return btn;
}
```

GOOD:
```cpp
#include <nana/gui.hpp>
#include <memory>
void setup_button(nana::form& fm) {
    auto btn = std::make_shared<nana::button>(fm, nana::rectangle(10, 10, 100, 30));
    btn->caption("Safe Button");
    auto weak_btn = std::weak_ptr<nana::button>(btn);
    btn->events().click([weak_btn]() {
        if (auto sp = weak_btn.lock()) {
            sp->caption("Clicked");
        }
    });
}
```

**Pitfall 4: Incorrect layout div syntax**

BAD:
```cpp
#include <nana/gui.hpp>
#include <nana/gui/place.hpp>
int main() {
    nana::form fm;
    nana::place layout(fm);
    nana::button btn(fm);
    
    layout.div("horiz <button>"); // Missing weight or size specification
    layout["button"] << btn;
    layout.collocate();
    
    fm.show();
    nana::exec();
}
```

GOOD:
```cpp
#include <nana/gui.hpp>
#include <nana/gui/place.hpp>
int main() {
    nana::form fm;
    nana::place layout(fm);
    nana::button btn(fm);
    btn.caption("OK");
    
    layout.div("vert <button weight=30>"); // Specify weight for sizing
    layout["button"] << btn;
    layout.collocate();
    
    fm.show();
    nana::exec();
}
```

**Pitfall 5: Not calling `collocate()` after modifying layout**

BAD:
```cpp
#include <nana/gui.hpp>
#include <nana/gui/place.hpp>
int main() {
    nana::form fm;
    nana::place layout(fm);
    nana::button btn(fm);
    
    layout.div("vert <button>");
    layout["button"] << btn;
    // Missing layout.collocate() - button won't be visible
    
    fm.show();
    nana::exec();
}
```

GOOD:
```cpp
#include <nana/gui.hpp>
#include <nana/gui/place.hpp>
int main() {
    nana::form fm;
    nana::place layout(fm);
    nana::button btn(fm);
    
    layout.div("vert <button>");
    layout["button"] << btn;
    layout.collocate(); // Required to apply layout
    
    fm.show();
    nana::exec();
}
```

**Pitfall 6: Using `nana::exec()` inside an event handler**

BAD:
```cpp
#include <nana/gui.hpp>
int main() {
    nana::form fm;
    nana::button btn(fm, nana::rectangle(10, 10, 100, 30));
    btn.caption("Exit");
    
    btn.events().click([&fm]() {
        nana::exec(); // Nested event loop - blocks UI
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
    btn.caption("Exit");
    
    btn.events().click([&fm]() {
        fm.close(); // Proper way to close window
    });
    
    fm.show();
    nana::exec();
}
```

**Pitfall 7: Ignoring widget parent ownership**

BAD:
```cpp
#include <nana/gui.hpp>
int main() {
    nana::form fm1;
    nana::form fm2;
    nana::button btn(fm1, nana::rectangle(10, 10, 100, 30)); // Parent is fm1
    
    // Later trying to move button to fm2 - not supported
    // btn.parent(fm2); // No such method
    
    fm1.show();
    fm2.show();
    nana::exec();
}
```

GOOD:
```cpp
#include <nana/gui.hpp>
int main() {
    nana::form fm;
    nana::button btn(fm, nana::rectangle(10, 10, 100, 30));
    btn.caption("Button on fm");
    
    // Create new button for second form if needed
    nana::form fm2;
    nana::button btn2(fm2, nana::rectangle(10, 10, 100, 30));
    btn2.caption("Button on fm2");
    
    fm.show();
    fm2.show();
    nana::exec();
}
```