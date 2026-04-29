# Quickstart

```cpp
// Basic command with subcommands
#include <cobra/cobra.hpp>
#include <iostream>

int main() {
    cobra::Command root;
    root.Use("app");
    root.Short("A sample CLI application");

    cobra::Command* greet = root.AddCommand("greet");
    greet->Short("Greet someone");
    greet->Run([](const cobra::Command& cmd, const std::vector<std::string>& args) {
        std::cout << "Hello, " << (args.empty() ? "World" : args[0]) << "!\n";
    });

    root.Execute();
    return 0;
}
```

```cpp
// Flags and persistent flags
#include <cobra/cobra.hpp>
#include <iostream>

int main() {
    cobra::Command root;
    root.Use("app");
    root.PersistentFlags().String("verbose", "v", "", "Enable verbose output");

    cobra::Command* serve = root.AddCommand("serve");
    serve->Flags().Int("port", "p", 8080, "Port to listen on");
    serve->Run([](const cobra::Command& cmd, const std::vector<std::string>& args) {
        bool verbose = cmd.Root().PersistentFlags().GetBool("verbose");
        int port = cmd.Flags().GetInt("port");
        std::cout << "Serving on port " << port 
                  << (verbose ? " (verbose)" : "") << "\n";
    });

    root.Execute();
    return 0;
}
```

```cpp
// Required flags and validation
#include <cobra/cobra.hpp>
#include <iostream>
#include <stdexcept>

int main() {
    cobra::Command root;
    root.Use("deploy");
    
    cobra::Command* deploy = root.AddCommand("service");
    deploy->Flags().String("name", "n", "", "Service name (required)");
    deploy->Flags().MarkRequired("name");
    deploy->Flags().Int("replicas", "r", 1, "Number of replicas");
    
    deploy->Run([](const cobra::Command& cmd, const std::vector<std::string>& args) {
        std::string name = cmd.Flags().GetString("name");
        int replicas = cmd.Flags().GetInt("replicas");
        std::cout << "Deploying " << name << " with " << replicas << " replicas\n";
    });

    root.Execute();
    return 0;
}
```

```cpp
// Command aliases and help
#include <cobra/cobra.hpp>
#include <iostream>

int main() {
    cobra::Command root;
    root.Use("cli");
    root.Short("CLI tool with aliases");

    cobra::Command* list = root.AddCommand("list");
    list->Aliases({"ls", "show"});
    list->Short("List items");
    list->Long("List all available items in the system with details");
    list->Run([](const cobra::Command& cmd, const std::vector<std::string>& args) {
        std::cout << "Listing items...\n";
    });

    root.Execute();
    return 0;
}
```

```cpp
// Subcommand groups and help
#include <cobra/cobra.hpp>
#include <iostream>

int main() {
    cobra::Command root;
    root.Use("tool");
    root.Short("Tool with command groups");

    cobra::Command* config = root.AddGroup("config");
    config->Short("Configuration commands");

    cobra::Command* get = config->AddCommand("get");
    get->Short("Get a config value");
    get->Run([](const cobra::Command& cmd, const std::vector<std::string>& args) {
        std::cout << "Getting config...\n";
    });

    cobra::Command* set = config->AddCommand("set");
    set->Short("Set a config value");
    set->Run([](const cobra::Command& cmd, const std::vector<std::string>& args) {
        std::cout << "Setting config...\n";
    });

    root.Execute();
    return 0;
}
```