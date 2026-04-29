# Safety

**Condition 1: NEVER access flags before Execute() is called**
```cpp
// BAD: Accessing flags before execution
#include <cobra/cobra.hpp>
#include <iostream>

int main() {
    cobra::Command root;
    root.Use("app");
    root.Flags().String("name", "n", "", "Name");
    
    std::string name = root.Flags().GetString("name");  // CRASH: flags not parsed
    std::cout << name << "\n";
    
    root.Execute();
    return 0;
}

// GOOD: Only access flags in Run callback
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

**Condition 2: NEVER use the same FlagSet for multiple commands**
```cpp
// BAD: Sharing FlagSet between commands
#include <cobra/cobra.hpp>
#include <iostream>

int main() {
    cobra::Command root;
    root.Use("app");
    
    cobra::FlagSet sharedFlags;
    sharedFlags.String("name", "n", "", "Name");
    
    cobra::Command* cmd1 = root.AddCommand("cmd1");
    cmd1->SetFlags(sharedFlags);  // DANGEROUS: shared state
    
    cobra::Command* cmd2 = root.AddCommand("cmd2");
    cmd2->SetFlags(sharedFlags);  // Same shared state
    
    root.Execute();
    return 0;
}

// GOOD: Each command has its own flags
#include <cobra/cobra.hpp>
#include <iostream>

int main() {
    cobra::Command root;
    root.Use("app");
    
    cobra::Command* cmd1 = root.AddCommand("cmd1");
    cmd1->Flags().String("name", "n", "", "Name for cmd1");
    
    cobra::Command* cmd2 = root.AddCommand("cmd2");
    cmd2->Flags().String("name", "n", "", "Name for cmd2");
    
    root.Execute();
    return 0;
}
```

**Condition 3: NEVER call Execute() more than once**
```cpp
// BAD: Multiple Execute calls
#include <cobra/cobra.hpp>
#include <iostream>

int main() {
    cobra::Command root;
    root.Use("app");
    root.Run([](const cobra::Command& cmd, const std::vector<std::string>& args) {
        std::cout << "Running\n";
    });
    
    root.Execute();  // First call works
    root.Execute();  // CRASH: undefined behavior
    
    return 0;
}

// GOOD: Single Execute call
#include <cobra/cobra.hpp>
#include <iostream>

int main() {
    cobra::Command root;
    root.Use("app");
    root.Run([](const cobra::Command& cmd, const std::vector<std::string>& args) {
        std::cout << "Running\n";
    });
    
    root.Execute();  // Only call once
    return 0;
}
```

**Condition 4: NEVER modify command hierarchy after Execute()**
```cpp
// BAD: Adding commands after execution
#include <cobra/cobra.hpp>
#include <iostream>

int main() {
    cobra::Command root;
    root.Use("app");
    root.Execute();
    
    root.AddCommand("newcmd");  // CRASH: modifying after execution
    
    return 0;
}

// GOOD: Build hierarchy before execution
#include <cobra/cobra.hpp>
#include <iostream>

int main() {
    cobra::Command root;
    root.Use("app");
    root.AddCommand("cmd1");
    root.AddCommand("cmd2");
    root.Execute();
    return 0;
}
```

**Condition 5: NEVER use dangling pointers to commands**
```cpp
// BAD: Using pointer after command is destroyed
#include <cobra/cobra.hpp>
#include <iostream>

int main() {
    cobra::Command* cmd = nullptr;
    {
        cobra::Command root;
        root.Use("app");
        cmd = root.AddCommand("sub");
        cmd->Short("Subcommand");
    }  // root destroyed, cmd is dangling
    
    cmd->Short("Still using");  // CRASH: dangling pointer
    
    return 0;
}

// GOOD: Commands are owned by their parent
#include <cobra/cobra.hpp>
#include <iostream>

int main() {
    cobra::Command root;
    root.Use("app");
    cobra::Command* cmd = root.AddCommand("sub");
    cmd->Short("Subcommand");
    
    root.Execute();  // root owns cmd, safe to use
    return 0;
}
```