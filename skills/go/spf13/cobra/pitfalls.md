# Pitfalls

```cpp
// BAD: Not checking if flags were provided
#include <cobra/cobra.hpp>
#include <iostream>

int main() {
    cobra::Command root;
    root.Use("app");
    root.Flags().String("name", "n", "", "Name");
    root.Run([](const cobra::Command& cmd, const std::vector<std::string>& args) {
        std::string name = cmd.Flags().GetString("name");  // Returns empty string if not set
        std::cout << "Name: " << name << "\n";  // Prints empty name
    });
    root.Execute();
    return 0;
}

// GOOD: Check if flag was provided
#include <cobra/cobra.hpp>
#include <iostream>
#include <stdexcept>

int main() {
    cobra::Command root;
    root.Use("app");
    root.Flags().String("name", "n", "", "Name");
    root.Run([](const cobra::Command& cmd, const std::vector<std::string>& args) {
        if (!cmd.Flags().IsSet("name")) {
            throw std::runtime_error("--name is required");
        }
        std::string name = cmd.Flags().GetString("name");
        std::cout << "Name: " << name << "\n";
    });
    root.Execute();
    return 0;
}
```

```cpp
// BAD: Using flags after command execution
#include <cobra/cobra.hpp>
#include <iostream>

int main() {
    cobra::Command root;
    root.Use("app");
    root.Flags().String("name", "n", "", "Name");
    root.Execute();  // Flags are parsed here
    
    // Trying to access flags after execution
    std::string name = root.Flags().GetString("name");  // Undefined behavior
    std::cout << name << "\n";
    return 0;
}

// GOOD: Access flags only in Run callback
#include <cobra/cobra.hpp>
#include <iostream>

int main() {
    cobra::Command root;
    root.Use("app");
    root.Flags().String("name", "n", "", "Name");
    root.Run([](const cobra::Command& cmd, const std::vector<std::string>& args) {
        std::string name = cmd.Flags().GetString("name");
        std::cout << name << "\n";
    });
    root.Execute();
    return 0;
}
```

```cpp
// BAD: Modifying flags after adding to command
#include <cobra/cobra.hpp>
#include <iostream>

int main() {
    cobra::Command root;
    root.Use("app");
    auto& flags = root.Flags();
    flags.String("name", "n", "", "Name");
    
    // Later modifying the flag
    flags.String("name", "n", "default", "Name");  // May cause issues
    
    root.Execute();
    return 0;
}

// GOOD: Define flags once
#include <cobra/cobra.hpp>
#include <iostream>

int main() {
    cobra::Command root;
    root.Use("app");
    root.Flags().String("name", "n", "default", "Name");
    root.Run([](const cobra::Command& cmd, const std::vector<std::string>& args) {
        std::string name = cmd.Flags().GetString("name");
        std::cout << name << "\n";
    });
    root.Execute();
    return 0;
}
```

```cpp
// BAD: Not handling errors from Execute
#include <cobra/cobra.hpp>
#include <iostream>

int main() {
    cobra::Command root;
    root.Use("app");
    root.Run([](const cobra::Command& cmd, const std::vector<std::string>& args) {
        std::cout << "Running\n";
    });
    root.Execute();  // Ignores errors
    return 0;
}

// GOOD: Handle errors properly
#include <cobra/cobra.hpp>
#include <iostream>
#include <cstdlib>

int main() {
    cobra::Command root;
    root.Use("app");
    root.Run([](const cobra::Command& cmd, const std::vector<std::string>& args) {
        std::cout << "Running\n";
    });
    
    try {
        root.Execute();
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
```