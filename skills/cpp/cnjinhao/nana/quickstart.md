# Quickstart

```cpp
#include <nana/gui.hpp>
#include <nana/gui/widgets/button.hpp>
#include <nana/gui/widgets/textbox.hpp>
#include <nana/gui/widgets/label.hpp>
#include <nana/gui/place.hpp>
#include <iostream>

// Pattern 1: Basic window with form
int main_basic_window()
{
    nana::form fm;
    fm.caption("Hello Nana");
    fm.show();
    nana::exec();
    return 0;
}

// Pattern 2: Button with event handler
int main_button_event()
{
    nana::form fm;
    nana::button btn(fm, nana::rectangle(10, 10, 100, 30));
    btn.caption("Click Me");
    
    btn.events().click([&fm]() {
        nana::msgbox mb(fm, "Event");
        mb << "Button clicked!";
        mb.show();
    });
    
    fm.show();
    nana::exec();
    return 0;
}

// Pattern 3: Textbox for input
int main_textbox()
{
    nana::form fm;
    nana::textbox txt(fm, nana::rectangle(10, 10, 200, 100));
    txt.append("Enter text here...");
    
    nana::button btn(fm, nana::rectangle(10, 120, 100, 30));
    btn.caption("Get Text");
    
    btn.events().click([&txt]() {
        std::string content = txt.text();
        nana::msgbox mb(txt.parent(), "Content");
        mb << "Text: " << content;
        mb.show();
    });
    
    fm.show();
    nana::exec();
    return 0;
}

// Pattern 4: Layout with place
int main_layout()
{
    nana::form fm;
    nana::place layout(fm);
    
    nana::label lbl(fm);
    lbl.caption("Welcome to Nana");
    
    nana::button btn(fm);
    btn.caption("OK");
    
    layout.div("vert <label weight=30> <button>");
    layout["label"] << lbl;
    layout["button"] << btn;
    layout.collocate();
    
    fm.show();
    nana::exec();
    return 0;
}

// Pattern 5: Multiple widgets with grid layout
int main_grid_layout()
{
    nana::form fm;
    nana::place layout(fm);
    
    nana::label lbl1(fm), lbl2(fm);
    nana::textbox txt1(fm), txt2(fm);
    nana::button btn(fm);
    
    lbl1.caption("Name:");
    lbl2.caption("Email:");
    btn.caption("Submit");
    
    layout.div("vert <grid=[2,2] gap=5 <lbl1> <txt1> <lbl2> <txt2>> <btn>");
    layout["lbl1"] << lbl1;
    layout["txt1"] << txt1;
    layout["lbl2"] << lbl2;
    layout["txt2"] << txt2;
    layout["btn"] << btn;
    layout.collocate();
    
    fm.show();
    nana::exec();
    return 0;
}

// Pattern 6: Timer for periodic tasks
#include <nana/gui/timer.hpp>
int main_timer()
{
    nana::form fm;
    nana::label lbl(fm, nana::rectangle(10, 10, 200, 30));
    lbl.caption("Timer: 0");
    
    nana::timer tmr;
    tmr.elapse([&lbl, count = 0]() mutable {
        lbl.caption("Timer: " + std::to_string(++count));
    });
    tmr.interval(std::chrono::milliseconds(1000));
    tmr.start();
    
    fm.show();
    nana::exec();
    return 0;
}

// Pattern 7: Drawing on a widget
#include <nana/gui/drawing.hpp>
int main_drawing()
{
    nana::form fm;
    nana::paint::graphics graph(fm.size());
    
    nana::drawing dw(fm);
    dw.draw([&graph](nana::paint::graphics& g) {
        g.rectangle(true, nana::colors::white);
        g.line({10, 10}, {100, 100}, nana::colors::red);
        g.circle({50, 50}, 30, nana::colors::blue, true);
    });
    
    fm.show();
    nana::exec();
    return 0;
}

// Pattern 8: File dialog
#include <nana/gui/filebox.hpp>
int main_filedialog()
{
    nana::form fm;
    nana::button btn(fm, nana::rectangle(10, 10, 100, 30));
    btn.caption("Open File");
    
    btn.events().click([&fm]() {
        nana::filebox fb(fm, true); // true = open file
        fb.add_filter("Text Files", "*.txt");
        fb.add_filter("All Files", "*.*");
        
        if (fb.show()) {
            auto files = fb.result();
            if (!files.empty()) {
                nana::msgbox mb(fm, "Selected");
                mb << "File: " << files[0];
                mb.show();
            }
        }
    });
    
    fm.show();
    nana::exec();
    return 0;
}
```