#include <fmt/format.h>
#include <fmt/ranges.h>
#include <vector>
#include <iostream>

struct User {
    std::string name;
    int age;
};

template <> struct fmt::formatter<User> {
    constexpr auto parse(fmt::format_parse_context& ctx) { return ctx.begin(); }
    auto format(const User& u, fmt::format_context& ctx) {
        return fmt::format_to(ctx.out(), "User({}, {})", u.name, u.age);
    }
};

int main() {
    // Basic formatting
    fmt::print("Hello, {}!\n", "world");

    // Positional and named arguments
    fmt::print("{1} {0}\n", "world", "Hello");
    fmt::print("{name} is {age} years old\n",
        fmt::arg("name", "Alice"), fmt::arg("age", 30));

    // Number formatting
    fmt::print("{:.2f}\n", 3.14159);       // 3.14
    fmt::print("{:04d}\n", 42);            // 0042
    fmt::print("{:#x}\n", 255);            // 0xff
    fmt::print("{:.2e}\n", 1.23e8);        // 1.23e+08

    // Container formatting
    std::vector<int> v = {1, 2, 3, 4, 5};
    fmt::print("v = {}\n", v);             // v = [1, 2, 3, 4, 5]
    fmt::print("v = [{}]\n", fmt::join(v, ", ")); // v = [1, 2, 3, 4, 5]

    // Custom type formatting
    User alice{"Alice", 30};
    fmt::print("{}\n", alice);             // User(Alice, 30)

    // Format to string
    std::string msg = fmt::format("Formatted at {}", std::time(nullptr));
    std::cout << msg << std::endl;

    return 0;
}
