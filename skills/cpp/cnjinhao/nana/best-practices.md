# Best Practices

**Practice 1: Use RAII for widget management**

```cpp
#include <nana/gui.hpp>
#include <nana/gui/widgets/button.hpp>
#include <memory>

class MyWindow {
    nana::form fm;
    std::unique_ptr<nana::button> btn;
    
public:
    MyWindow() 
        : fm()
        , btn(std::make_unique<nana::button>(fm, nana::rectangle(10, 10, 100, 30)))
    {
        btn->caption("Click Me");
        btn->events().click([this]() {
            on_click();
        });
        fm.show();
    }
    
    void run() {
        nana::exec();
    }
    
private:
    void on_click() {
        nana::msgbox mb(fm, "Info");
        mb << "Button clicked!";
        mb.show();
    }
};

int main() {
    MyWindow app;
    app.run();
}
```

**Practice 2: Use `nana::place` for responsive layouts**

```cpp
#include <nana/gui.hpp>
#include <nana/gui/place.hpp>
#include <nana/gui/widgets/button.hpp>
#include <nana/gui/widgets/textbox.hpp>
#include <nana/gui/widgets/label.hpp>

class ResponsiveWindow {
    nana::form fm;
    nana::place layout;
    nana::label title;
    nana::textbox input;
    nana::button submit;
    
public:
    ResponsiveWindow()
        : fm(nana::size(400, 300))
        , layout(fm)
        , title(fm)
        , input(fm)
        , submit(fm)
    {
        fm.caption("Responsive App");
        title.caption("Enter your name:");
        submit.caption("Submit");
        
        // Use flexible layout with weight ratios
        layout.div("vert <title weight=20> <input weight=60> <submit weight=20>");
        layout["title"] << title;
        layout["input"] << input;
        layout["submit"] << submit;
        layout.collocate();
        
        submit.events().click([this]() {
            on_submit();
        });
        
        fm.show();
    }
    
    void run() { nana::exec(); }
    
private:
    void on_submit() {
        std::string name = input.text();
        if (!name.empty()) {
            title.caption("Hello, " + name + "!");
        }
    }
};
```

**Practice 3: Use timers for periodic UI updates**

```cpp
#include <nana/gui.hpp>
#include <nana/gui/timer.hpp>
#include <nana/gui/widgets/label.hpp>
#include <chrono>

class ClockWindow {
    nana::form fm;
    nana::label clock_label;
    nana::timer timer;
    
public:
    ClockWindow()
        : fm(nana::size(300, 100))
        , clock_label(fm, nana::rectangle(10, 10, 280, 80))
        , timer()
    {
        fm.caption("Digital Clock");
        clock_label.text_align(nana::align::center, nana::align_v::center);
        clock_label.typeface(nana::paint::font("", 24));
        
        timer.elapse([this]() {
            update_clock();
        });
        timer.interval(std::chrono::seconds(1));
        timer.start();
        
        update_clock(); // Initial display
        fm.show();
    }
    
    void run() { nana::exec(); }
    
private:
    void update_clock() {
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);
        std::string time_str = std::ctime(&time_t);
        time_str.pop_back(); // Remove newline
        clock_label.caption(time_str);
    }
};
```

**Practice 4: Handle errors gracefully with message boxes**

```cpp
#include <nana/gui.hpp>
#include <nana/gui/widgets/button.hpp>
#include <nana/gui/filebox.hpp>
#include <fstream>
#include <iostream>

class FileLoader {
    nana::form fm;
    nana::button load_btn;
    nana::label status;
    
public:
    FileLoader()
        : fm(nana::size(400, 200))
        , load_btn(fm, nana::rectangle(10, 10, 100, 30))
        , status(fm, nana::rectangle(10, 50, 380, 100))
    {
        fm.caption("File Loader");
        load_btn.caption("Load File");
        status.caption("Ready");
        
        load_btn.events().click([this]() {
            try {
                load_file();
            } catch (const std::exception& e) {
                nana::msgbox mb(fm, "Error");
                mb.icon(mb.icon_error);
                mb << "Failed to load file:\n" << e.what();
                mb.show();
                status.caption("Error: " + std::string(e.what()));
            }
        });
        
        fm.show();
    }
    
    void run() { nana::exec(); }
    
private:
    void load_file() {
        nana::filebox fb(fm, true);
        fb.add_filter("Text Files", "*.txt");
        fb.add_filter("All Files", "*.*");
        
        if (!fb.show()) return;
        
        auto files = fb.result();
        if (files.empty()) return;
        
        std::ifstream file(files[0].string());
        if (!file.is_open()) {
            throw std::runtime_error("Cannot open file: " + files[0].string());
        }
        
        std::string content((std::istreambuf_iterator<char>(file)),
                             std::istreambuf_iterator<char>());
        status.caption("Loaded: " + files[0].filename().string() + 
                       " (" + std::to_string(content.size()) + " bytes)");
    }
};
```

**Practice 5: Use `nana::paint::graphics` for custom drawing**

```cpp
#include <nana/gui.hpp>
#include <nana/gui/drawing.hpp>
#include <nana/gui/widgets/label.hpp>
#include <cmath>

class GraphWidget {
    nana::form fm;
    nana::drawing dw;
    std::vector<nana::point> data_points;
    
public:
    GraphWidget()
        : fm(nana::size(500, 400))
        , dw(fm)
    {
        fm.caption("Graph Demo");
        
        // Generate sample data
        for (int x = 0; x <= 400; x += 10) {
            double y = 100 + 50 * std::sin(x * 0.05);
            data_points.push_back({x + 50, static_cast<int>(y)});
        }
        
        dw.draw([this](nana::paint::graphics& g) {
            draw_graph(g);
        });
        
        fm.show();
    }
    
    void run() { nana::exec(); }
    
private:
    void draw_graph(nana::paint::graphics& g) {
        // Clear background
        g.rectangle(true, nana::colors::white);
        
        // Draw axes
        g.line({50, 50}, {50, 350}, nana::colors::black);
        g.line({50, 200}, {450, 200}, nana::colors::black);
        
        // Draw data points
        if (data_points.size() < 2) return;
        
        for (size_t i = 1; i < data_points.size(); ++i) {
            g.line(data_points[i-1], data_points[i], nana::colors::blue);
        }
        
        // Draw labels
        nana::paint::font orig_font = g.typeface();
        g.typeface(nana::paint::font("", 12));
        g.string({60, 210}, "X Axis", nana::colors::black);
        g.string({10, 100}, "Y Axis", nana::colors::black);
        g.typeface(orig_font);
    }
};
```