#include <spdlog/spdlog.h>
#include <spdlog/sinks/rotating_file_sink.h>
#include <spdlog/async.h>

int main() {
    // Setup: async logger with rotating file sink
    spdlog::init_thread_pool(8192, 1);
    auto sink = std::make_shared<spdlog::sinks::rotating_file_sink_mt>(
        "logs/app.log", 1048576 * 5, 3);
    auto logger = std::make_shared<spdlog::async_logger>(
        "app", sink, spdlog::thread_pool(),
        spdlog::async_overflow_policy::block);
    logger->set_pattern("[%Y-%m-%d %H:%M:%S.%e] [%^%l%$] [%t] %v");
    logger->set_level(spdlog::level::info);
    spdlog::set_default_logger(logger);

    // Usage
    spdlog::info("Application started");
    spdlog::debug("Debug info (won't appear at info level)");
    spdlog::warn("Warning: something might be wrong");

    int user_id = 42;
    spdlog::info("User {} logged in", user_id);

    try {
        throw std::runtime_error("simulated error");
    } catch (const std::exception& e) {
        spdlog::error("Caught exception: {}", e.what());
    }

    // Shutdown: must be called before exit, NOT in a static destructor
    spdlog::shutdown();
    return 0;
}
