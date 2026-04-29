# Overview

Celery is a distributed task queue library for C++ that allows you to execute tasks asynchronously across multiple workers or machines. It provides a simple API for defining, scheduling, and monitoring tasks, with support for various message brokers (Redis, RabbitMQ) and result backends.

**When to use Celery:**
- You need to offload long-running or CPU-intensive tasks from your main application
- You want to implement asynchronous processing with retry and error handling
- You need to distribute work across multiple machines or processes
- You require task scheduling with delays, periodic execution, or chaining

**When NOT to use Celery:**
- For simple synchronous operations that don't benefit from async execution
- When you need real-time processing with sub-millisecond latency
- For tasks that must execute in a specific order with strict guarantees
- When your application doesn't need distributed processing

**Key design principles:**
- Task-based architecture: Tasks are self-contained units of work
- Broker abstraction: Supports multiple message brokers transparently
- Result backends: Flexible storage for task results
- Task routing: Control which workers execute specific tasks
- Error handling: Built-in retry mechanisms and exception propagation