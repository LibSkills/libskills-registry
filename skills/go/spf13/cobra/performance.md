# Performance

```cpp
// Performance characteristics
#include <cobra/cobra.hpp>
#include <iostream>
#include <chrono>

int main() {
    // Flag parsing overhead: O(n) where n is number of flags
    cobra::Command root;
    root.Use("app");
    
    // Each flag adds parsing overhead
    root.Flags().String("name", "n", "", "Name");
    root.Flags().Int("count", "c", 1, "Count");
    root.Flags().Bool("verbose", "v", false, "Verbose");
    
    // Command lookup: O(log m) where m is number of subcommands
    cobra::Command* sub = root.AddCommand("sub");
    sub->Short("Subcommand");
    
    root.Run([](const cobra::Command& cmd, const std::vector<std::string>& args) {
        auto start = std::chrono::high_resolution_clock::now();
        
        // Flag access is O(1) after parsing
        std::string name = cmd.Flags().GetString("name");
        int count = cmd.Flags().GetInt("count");
        
        auto end = std::chrono::high_resolution_clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
        std::cout << "Flag access took: " << duration.count() << " us\n";
    });
    
    root.Execute();
    return 0;
}
```

```cpp
// Optimization: Minimize flag count
#include <cobra/cobra.hpp>
#include <iostream>

// BAD: Too many flags
int main() {
    cobra::Command root;
    root.Use("app");
    
    // Each flag adds parsing overhead
    for (int i = 0; i < 100; ++i) {
        root.Flags().String("flag" + std::to_string(i), "", "", "Flag " + std::to_string(i));
    }
    
    root.Run([](const cobra::Command& cmd, const std::vector<std::string>& args) {
        // Slow parsing for 100 flags
        std::cout << "Running\n";
    });
    
    root.Execute();
    return 0;
}

// GOOD: Use config file for many options
#include <cobra/cobra.hpp>
#include <iostream>
#include <fstream>
#include <nlohmann/json.hpp>

int main() {
    cobra::Command root;
    root.Use("app");
    
    // Only one flag for config file
    root.Flags().String("config", "c", "", "Path to config file");
    
    root.Run([](const cobra::Command& cmd, const std::vector<std::string>& args) {
        std::string configPath = cmd.Flags().GetString("config");
        if (!configPath.empty()) {
            std::ifstream file(configPath);
            nlohmann::json config;
            file >> config;
            // Use config values
        }
        std::cout << "Running\n";
    });
    
    root.Execute();
    return 0;
}
```

```cpp
// Allocation patterns
#include <cobra/cobra.hpp>
#include <iostream>
#include <vector>

int main() {
    cobra::Command root;
    root.Use("app");
    
    // Commands allocate internally
    // Each AddCommand creates a new allocation
    std::vector<cobra::Command*> commands;
    for (int i = 0; i < 10; ++i) {
        commands.push_back(root.AddCommand("cmd" + std::to_string(i)));
    }
    
    // Flags also allocate internally
    root.Flags().String("name", "n", "", "Name");
    
    root.Run([](const cobra::Command& cmd, const std::vector<std::string>& args) {
        // String flags allocate when accessed
        std::string name = cmd.Flags().GetString("name");  // Allocation
        
        // Bool flags don't allocate
        bool verbose = cmd.Flags().GetBool("verbose");  // No allocation
        
        std::cout << "Name: " << name << "\n";
    });
    
    root.Execute();
    return 0;
}
```