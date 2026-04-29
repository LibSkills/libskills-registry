# Safety

**Condition 1: NEVER block the executor thread with synchronous operations**
```cpp
// BAD: Blocking with std::this_thread::sleep
rt.spawn([]() {
    std::this_thread::sleep_for(std::chrono::seconds(1));
});

// GOOD: Use async sleep
rt.spawn([]() -> smol::task<void> {
    co_await smol::sleep(std::chrono::seconds(1));
});
```

**Condition 2: NEVER use smol objects across thread boundaries**
```cpp
// BAD: Sharing runtime across threads
smol::runtime rt;
std::thread t([&rt]() {
    rt.spawn([]() { /* ... */ }); // Undefined behavior!
});

// GOOD: Each thread gets its own runtime
std::thread t([]() {
    smol::runtime local_rt;
    local_rt.spawn([]() { /* ... */ });
    local_rt.run();
});
```

**Condition 3: NEVER forget to co_await async operations**
```cpp
// BAD: Missing co_await
smol::task<int> task = compute_value(); // Task created but not awaited

// GOOD: Properly await
int result = co_await compute_value();
```

**Condition 4: NEVER hold locks across await points**
```cpp
// BAD: Holding mutex across await
std::mutex mtx;
co_await async_operation(); // mtx still held!

// GOOD: Release lock before await
{
    std::lock_guard<std::mutex> lock(mtx);
    // Critical section
}
co_await async_operation(); // Lock released
```

**Condition 5: NEVER use smol after runtime destruction**
```cpp
// BAD: Using smol objects after runtime destroyed
smol::runtime* rt = new smol::runtime();
auto task = rt->spawn([]() { /* ... */ });
delete rt;
task.resume(); // Undefined behavior!

// GOOD: Ensure runtime outlives all tasks
smol::runtime rt;
auto task = rt.spawn([]() { /* ... */ });
rt.run(); // Runtime lives until all tasks complete
```