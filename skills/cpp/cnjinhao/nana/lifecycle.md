# Lifecycle

**Construction**

Widgets in Nana are constructed with a parent widget reference and optional position/size. The parent must outlive the child widget.

```cpp
#include <nana/gui.hpp>
#include <nana/gui/widgets/button.hpp>
#include <nana/gui/widgets/label.hpp>

// Basic construction
nana::form fm;  // Top-level window
nana::button btn(fm, nana::rectangle(10, 10, 100, 30));  // Child of fm
nana::label lbl(fm, nana::rectangle(10, 50, 200, 30));   // Another child

// Construction with default size
nana::button btn2(fm);  // Will be sized when placed in layout

// Construction with explicit size
nana::button btn3(fm, nana::size(150, 40));
```

**Destruction**

Widgets are automatically destroyed when their parent form is destroyed. Manual destruction is possible but must be done carefully.

```cpp
#include <nana/gui.hpp>
#include <nana/gui/widgets/button.hpp>
#include <memory>

class SafeWidgetManager {
    nana::form fm;
    std::vector<std::unique_ptr<nana::button>> buttons;
    
public:
    SafeWidgetManager() : fm() {
        // Widgets are managed by unique_ptr
        auto btn = std::make_unique<nana::button>(fm, nana::rectangle(10, 10, 100, 30));
        btn->caption("Button 1");
        buttons.push_back(std::move(btn));
        
        // Another button
        auto btn2 = std::make_unique<nana::button>(fm, nana::rectangle(10, 50, 100, 30));
        btn2->caption("Button 2");
        buttons.push_back(std::move(btn2));
        
        fm.show();
    }
    
    // When SafeWidgetManager is destroyed, buttons vector is destroyed first,
    // then fm is destroyed, which properly cleans up all child widgets
    
    void run() { nana::exec(); }
};
```

**Move Semantics**

Nana widgets support move semantics, but with important caveats. After moving, the source widget should not be used.

```cpp
#include <nana/gui.hpp>
#include <nana/gui/widgets/button.hpp>

void move_example() {
    nana::form fm;
    
    // Create a button
    nana::button btn1(fm, nana::rectangle(10, 10, 100, 30));
    btn1.caption("Original");
    
    // Move construct - btn1 is now in a valid but unspecified state
    nana::button btn2(std::move(btn1));
    btn2.caption("Moved");  // btn2 now owns the widget
    
    // btn1 should not be used after move
    // btn1.caption("Don't do this"); // Undefined behavior
    
    // Move assignment
    nana::button btn3(fm, nana::rectangle(10, 50, 100, 30));
    btn3 = std::move(btn2);  // btn3 takes ownership, btn2 is invalidated
    
    fm.show();
    nana::exec();
}
```

**Resource Management**

Proper resource management ensures no memory leaks or dangling references.

```cpp
#include <nana/gui.hpp>
#include <nana/gui/widgets/button.hpp>
#include <nana/gui/widgets/label.hpp>
#include <vector>
#include <memory>

class ResourceManager {
    nana::form fm;
    nana::label status;
    std::vector<std::shared_ptr<nana::button>> dynamic_buttons;
    
public:
    ResourceManager()
        : fm(nana::size(400, 300))
        , status(fm, nana::rectangle(10, 10, 380, 30))
    {
        fm.caption("Resource Manager");
        status.caption("Ready");
        
        // Create initial buttons
        for (int i = 0; i < 3; ++i) {
            add_button("Button " + std::to_string(i + 1));
        }
        
        fm.show();
    }
    
    void add_button(const std::string& caption) {
        auto btn = std::make_shared<nana::button>(
            fm, 
            nana::rectangle(10, 50 + 40 * dynamic_buttons.size(), 100, 30)
        );
        btn->caption(caption);
        
        // Use weak_ptr to avoid circular references in event handlers
        std::weak_ptr<nana::button> weak_btn = btn;
        btn->events().click([this, weak_btn]() {
            if (auto sp = weak_btn.lock()) {
                status.caption("Clicked: " + sp->caption());
            }
        });
        
        dynamic_buttons.push_back(btn);
    }
    
    void remove_last_button() {
        if (!dynamic_buttons.empty()) {
            dynamic_buttons.pop_back(); // Shared pointer releases the button
            status.caption("Removed last button");
        }
    }
    
    void run() { nana::exec(); }
    
    ~ResourceManager() {
        // Clean up in reverse order to avoid issues
        dynamic_buttons.clear();
        // fm destructor handles remaining cleanup
    }
};
```

**Lifetime Management with Event Handlers**

Event handlers that capture `this` must ensure the handler is disconnected before the object is destroyed.

```cpp
#include <nana/gui.hpp>
#include <nana/gui/widgets/button.hpp>
#include <memory>

class EventfulWidget {
    nana::form fm;
    nana::button btn;
    nana::label status;
    bool destroyed = false;
    
public:
    EventfulWidget()
        : fm(nana::size(300, 200))
        , btn(fm, nana::rectangle(10, 10, 100, 30))
        , status(fm, nana::rectangle(10, 50, 280, 100))
    {
        fm.caption("Eventful Widget");
        btn.caption("Click me");
        status.caption("Ready");
        
        // Safe capture: use weak pointer pattern
        auto weak_this = std::weak_ptr<EventfulWidget>(shared_from_this());
        btn.events().click([weak_this]() {
            if (auto sp = weak_this.lock()) {
                sp->status.caption("Button clicked at " + 
                    std::to_string(std::time(nullptr)));
            }
        });
        
        fm.show();
    }
    
    void run() { nana::exec(); }
    
    ~EventfulWidget() {
        destroyed = true;
        // Event handlers are automatically disconnected when fm is destroyed
    }
    
private:
    std::shared_ptr<EventfulWidget> shared_from_this() {
        return std::shared_ptr<EventfulWidget>(this, [](EventfulWidget*) {});
    }
};
```