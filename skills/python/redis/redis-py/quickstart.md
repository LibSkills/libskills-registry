# Quickstart

```cpp
#include <sw/redis++/redis++.h>
#include <iostream>
#include <string>
#include <vector>

using namespace sw::redis;

// Pattern 1: Basic connection and SET/GET
void basic_operations() {
    auto redis = Redis("tcp://127.0.0.1:6379");
    
    redis.set("key", "value");
    auto val = redis.get("key");
    if (val) {
        std::cout << *val << std::endl;  // Output: value
    }
}

// Pattern 2: Working with hashes
void hash_operations() {
    auto redis = Redis("tcp://127.0.0.1:6379");
    
    redis.hset("user:1", "name", "Alice");
    redis.hset("user:1", "age", "30");
    
    auto name = redis.hget("user:1", "name");
    auto all_fields = redis.hgetall("user:1");
}

// Pattern 3: Lists and queues
void list_operations() {
    auto redis = Redis("tcp://127.0.0.1:6379");
    
    redis.lpush("queue", "task1");
    redis.lpush("queue", "task2");
    auto task = redis.rpop("queue");
}

// Pattern 4: Pipelining for batch operations
void pipelining_example() {
    auto redis = Redis("tcp://127.0.0.1:6379");
    
    auto pipe = redis.pipeline();
    auto reply1 = pipe.set("key1", "val1");
    auto reply2 = pipe.set("key2", "val2");
    auto reply3 = pipe.get("key1");
    pipe.exec();
}

// Pattern 5: Transactions with MULTI/EXEC
void transaction_example() {
    auto redis = Redis("tcp://127.0.0.1:6379");
    
    auto tx = redis.transaction();
    tx.set("key", "value");
    tx.incr("counter");
    tx.exec();
}

// Pattern 6: Subscriptions
void subscription_example() {
    auto redis = Redis("tcp://127.0.0.1:6379");
    
    auto sub = redis.subscriber();
    sub.subscribe("channel1");
    
    sub.on_message([](std::string channel, std::string msg) {
        std::cout << "Received: " << msg << std::endl;
    });
    
    sub.consume();
}

int main() {
    basic_operations();
    hash_operations();
    list_operations();
    return 0;
}
```