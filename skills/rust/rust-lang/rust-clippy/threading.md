# Threading

```markdown
# Thread Safety with rust-lang/rust-clippy

## Thread Safety Guarantees

Clippy itself is **not thread-safe** for concurrent analysis. Each invocation should run in a single thread. However, Clippy helps ensure your code is thread-safe.

## Send and Sync Traits

### BAD: Non-thread-safe code

```rust
use std::rc::Rc;
use std::thread;

fn main() {
    let data = Rc::new(42);
    thread::spawn(move || {
        println!("{}", data); // Error: Rc is not Send
    });
}
```

### GOOD: Thread-safe alternatives

```rust
use std::sync::Arc;
use std::thread;

fn main() {
    let data = Arc::new(42);
    thread::spawn(move || {
        println!("{}", data); // Arc is Send + Sync
    });
}
```

## Mutex Usage Patterns

### BAD: Holding lock across await points

```rust
use std::sync::Mutex;

async fn process_data(data: Mutex<Vec<i32>>) {
    let mut guard = data.lock().unwrap();
    // Clippy warns: holding lock across await
    some_async_function().await;
    guard.push(42);
}
```

### GOOD: Minimize lock scope

```rust
use std::sync::Mutex;

async fn process_data(data: Mutex<Vec<i32>>) {
    let value = {
        let mut guard = data.lock().unwrap();
        guard.pop()
    };
    some_async_function().await;
    if let Some(v) = value {
        let mut guard = data.lock().unwrap();
        guard.push(v);
    }
}
```

## Atomic Operations

### BAD: Using Mutex for simple counters

```rust
use std::sync::Mutex;

struct Counter {
    value: Mutex<i32>,
}

impl Counter {
    fn increment(&self) {
        let mut guard = self.value.lock().unwrap();
        *guard += 1;
    }
}
```

### GOOD: Use atomics for simple operations

```rust
use std::sync::atomic::{AtomicI32, Ordering};

struct Counter {
    value: AtomicI32,
}

impl Counter {
    fn increment(&self) {
        self.value.fetch_add(1, Ordering::SeqCst);
    }
}
```

## Concurrent Data Structures

### BAD: Using Vec in shared state

```rust
use std::sync::Mutex;

struct SharedState {
    data: Mutex<Vec<i32>>,
}

// Clippy warns about potential deadlocks
```

### GOOD: Use appropriate concurrent structures

```rust
use std::sync::Mutex;

struct SharedState {
    data: Mutex<Vec<i32>>,
}

impl SharedState {
    fn add_item(&self, item: i32) {
        let mut guard = self.data.lock().unwrap();
        guard.push(item);
        // Lock released when guard drops
    }
}
```

## Thread Local Storage

### BAD: Using global mutable state

```rust
static mut COUNTER: i32 = 0; // Unsafe!

fn increment() {
    unsafe {
        COUNTER += 1;
    }
}
```

### GOOD: Use thread-local storage

```rust
use std::cell::RefCell;

thread_local! {
    static COUNTER: RefCell<i32> = RefCell::new(0);
}

fn increment() {
    COUNTER.with(|c| {
        *c.borrow_mut() += 1;
    });
}
```

## Clippy Lints for Thread Safety

| Lint | Description | Severity |
|------|-------------|----------|
| `clippy::mutex_atomic` | Suggests using atomics instead of Mutex | Warning |
| `clippy::await_holding_lock` | Warns about holding locks across await | Warning |
| `clippy::send_sync` | Checks Send/Sync implementations | Warning |
| `clippy::thread_local` | Suggests thread-local alternatives | Style |

## Best Practices for Concurrent Code

```rust
use std::sync::{Arc, Mutex};
use std::thread;

// Thread-safe shared state
struct SharedCounter {
    counter: Mutex<i32>,
}

impl SharedCounter {
    fn new() -> Self {
        SharedCounter {
            counter: Mutex::new(0),
        }
    }

    fn increment(&self) {
        let mut guard = self.counter.lock().unwrap();
        *guard += 1;
    }

    fn get(&self) -> i32 {
        *self.counter.lock().unwrap()
    }
}

fn main() {
    let counter = Arc::new(SharedCounter::new());
    let mut handles = vec![];

    for _ in 0..10 {
        let counter = Arc::clone(&counter);
        handles.push(thread::spawn(move || {
            for _ in 0..100 {
                counter.increment();
            }
        }));
    }

    for handle in handles {
        handle.join().unwrap();
    }

    println!("Final count: {}", counter.get());
}
```
```