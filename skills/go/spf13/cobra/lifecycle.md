# Lifecycle

```cpp
// Construction and destruction
#include <cobra/cobra.hpp>
#include <iostream>
#include <memory>

int main() {
    // Default construction
    cobra::Command root;
    root.Use("app");
    
    // Commands are owned by their parent
    cobra::Command* sub = root.AddCommand("sub");
    sub->Short("Subcommand");
    
    // When root is destroyed, all subcommands are destroyed too
    // No manual cleanup needed
    
    root.Execute();
    return 0;
}  // root destroyed here, sub destroyed automatically
```

```cpp
// Move semantics
#include <cobra/cobra.hpp>
#include <iostream>
#include <utility>

int main() {
    cobra::Command root;
    root.Use("app");
    
    // Move construction
    cobra::Command other;
    other.Use("other");
    root.AddCommand(std::move(other));  // Move into root
    
    // After move, other is in valid but unspecified state
    // Don't use other after moving
    
    root.Execute();
    return 0;
}
```

```cpp
// Resource management with unique_ptr
#include <cobra/cobra.hpp>
#include <iostream>
#include <memory>

std::unique_ptr<cobra::Command> CreateCommand() {
    auto cmd = std::make_unique<cobra::Command>();
    cmd->Use("dynamic");
    cmd->Short("Dynamically created command");
    return cmd;
}

int main() {
    cobra::Command root;
    root.Use("app");
    
    // Transfer ownership via raw pointer
    root.AddCommand(CreateCommand().release());
    
    // Or use AddCommand with unique_ptr
    auto cmd = std::make_unique<cobra::Command>();
    cmd->Use("another");
    root.AddCommand(cmd.release());
    
    root.Execute();
    return 0;
}
```

```cpp
// Lifetime management with shared_ptr
#include <cobra/cobra.hpp>
#include <iostream>
#include <memory>

int main() {
    auto root = std::make_shared<cobra::Command>();
    root->Use("app");
    
    // Commands hold shared_ptr to parent
    cobra::Command* sub = root->AddCommand("sub");
    sub->Short("Subcommand");
    
    // root keeps sub alive
    // sub has a reference to root
    
    root->Execute();
    return 0;
}
```