# Overview

```cpp
// Overview: spf13/viper - Configuration Management Library

/*
 * What viper does:
 * - Reads configuration from multiple sources (files, environment, remote)
 * - Supports multiple config formats (JSON, YAML, TOML, HCL, INI, envfile)
 * - Provides hierarchical key-value access with dot notation
 * - Supports default values, environment variable binding
 * - Can watch for config file changes
 * - Merges configuration from multiple sources with priority
 */

/*
 * When to use viper:
 * - Applications needing flexible configuration from multiple sources
 * - Microservices that need environment-specific configuration
 * - CLI tools that support config files and environment variables
 * - Applications requiring runtime config reloading
 * 
 * When NOT to use viper:
 * - Simple applications with static configuration
 * - Performance-critical paths (viper has overhead)
 * - When you need compile-time configuration validation
 * - When configuration is purely command-line arguments
 */

/*
 * Key design principles:
 * 1. Priority order (highest to lowest):
 *    - Explicit calls to Set()
 *    - Environment variables
 *    - Config file
 *    - Key/value store
 *    - Defaults
 * 
 * 2. Hierarchical key access using dot notation
 * 3. Type-safe getters with optional defaults
 * 4. Immutable after reading (unless explicitly modified)
 */

#include <viper/viper.hpp>
#include <iostream>

// Example demonstrating priority
int main() {
    viper::Viper v;
    
    // Set defaults (lowest priority)
    v.set_default("port", 8080);
    v.set_default("host", "localhost");
    
    // Read config file (medium priority)
    v.set_config_name("config");
    v.set_config_type("yaml");
    v.add_config_path(".");
    v.read_in_config();
    
    // Environment variables override config (higher priority)
    v.bind_env("port", "APP_PORT");
    v.bind_env("host", "APP_HOST");
    
    // Explicit Set() calls (highest priority)
    v.set("port", 3000);  // This wins
    
    std::cout << "Final port: " << v.get_int("port") << "\n";
    return 0;
}
```