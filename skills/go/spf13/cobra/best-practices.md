# Best Practices

```cpp
// Use factory functions for complex commands
#include <cobra/cobra.hpp>
#include <iostream>
#include <memory>

class DeployCommand {
public:
    static std::unique_ptr<cobra::Command> Create() {
        auto cmd = std::make_unique<cobra::Command>();
        cmd->Use("deploy");
        cmd->Short("Deploy a service");
        cmd->Long("Deploy a service to the cluster with specified configuration");
        
        cmd->Flags().String("name", "n", "", "Service name");
        cmd->Flags().Int("replicas", "r", 1, "Number of replicas");
        cmd->Flags().MarkRequired("name");
        
        cmd->Run([](const cobra::Command& cmd, const std::vector<std::string>& args) {
            std::string name = cmd.Flags().GetString("name");
            int replicas = cmd.Flags().GetInt("replicas");
            std::cout << "Deploying " << name << " with " << replicas << " replicas\n";
        });
        
        return cmd;
    }
};

int main() {
    cobra::Command root;
    root.Use("app");
    root.AddCommand(DeployCommand::Create().release());  // Transfer ownership
    root.Execute();
    return 0;
}
```

```cpp
// Consistent error handling pattern
#include <cobra/cobra.hpp>
#include <iostream>
#include <cstdlib>
#include <string>

int main(int argc, char* argv[]) {
    cobra::Command root;
    root.Use("app");
    root.Short("Application with consistent error handling");
    
    root.Run([](const cobra::Command& cmd, const std::vector<std::string>& args) {
        try {
            // Validate inputs
            if (args.empty()) {
                throw std::invalid_argument("Missing required argument");
            }
            
            // Process command
            std::cout << "Processing: " << args[0] << "\n";
            
        } catch (const std::exception& e) {
            std::cerr << "Error: " << e.what() << "\n";
            std::exit(EXIT_FAILURE);
        }
    });
    
    try {
        root.Execute();
    } catch (const std::exception& e) {
        std::cerr << "Fatal error: " << e.what() << "\n";
        return EXIT_FAILURE;
    }
    
    return EXIT_SUCCESS;
}
```

```cpp
// Use persistent flags for shared configuration
#include <cobra/cobra.hpp>
#include <iostream>

int main() {
    cobra::Command root;
    root.Use("app");
    root.PersistentFlags().String("config", "c", "", "Path to config file");
    root.PersistentFlags().Bool("verbose", "v", false, "Enable verbose output");
    
    cobra::Command* deploy = root.AddCommand("deploy");
    deploy->Short("Deploy service");
    deploy->Run([](const cobra::Command& cmd, const std::vector<std::string>& args) {
        std::string config = cmd.Root().PersistentFlags().GetString("config");
        bool verbose = cmd.Root().PersistentFlags().GetBool("verbose");
        
        if (verbose) {
            std::cout << "Using config: " << config << "\n";
        }
        std::cout << "Deploying...\n";
    });
    
    cobra::Command* status = root.AddCommand("status");
    status->Short("Check status");
    status->Run([](const cobra::Command& cmd, const std::vector<std::string>& args) {
        bool verbose = cmd.Root().PersistentFlags().GetBool("verbose");
        std::cout << "Status: OK" << (verbose ? " (verbose)" : "") << "\n";
    });
    
    root.Execute();
    return 0;
}
```

```cpp
// Command validation and pre-run hooks
#include <cobra/cobra.hpp>
#include <iostream>
#include <regex>

int main() {
    cobra::Command root;
    root.Use("app");
    
    cobra::Command* create = root.AddCommand("create");
    create->Short("Create a resource");
    create->Flags().String("name", "n", "", "Resource name");
    create->Flags().MarkRequired("name");
    
    // Pre-run validation
    create->PreRun([](const cobra::Command& cmd, const std::vector<std::string>& args) {
        std::string name = cmd.Flags().GetString("name");
        std::regex validName("^[a-zA-Z][a-zA-Z0-9_-]*$");
        if (!std::regex_match(name, validName)) {
            throw std::invalid_argument("Invalid resource name: " + name);
        }
    });
    
    create->Run([](const cobra::Command& cmd, const std::vector<std::string>& args) {
        std::string name = cmd.Flags().GetString("name");
        std::cout << "Created resource: " << name << "\n";
    });
    
    root.Execute();
    return 0;
}
```