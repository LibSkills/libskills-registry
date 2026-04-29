# Quickstart

```cpp
// Basic HTTP server with routing
#include <drogon/drogon.h>
using namespace drogon;

int main() {
    // Register a simple GET handler
    app().registerHandler("/hello",
        [](const HttpRequestPtr& req,
           std::function<void(const HttpResponsePtr&)>&& callback) {
            auto resp = HttpResponse::newHttpResponse();
            resp->setBody("<h1>Hello, Drogon!</h1>");
            callback(resp);
        },
        {Get});

    // Start server on port 8080
    app().addListener("0.0.0.0", 8080).run();
    return 0;
}
```

```cpp
// JSON API endpoint
#include <drogon/drogon.h>
using namespace drogon;

int main() {
    app().registerHandler("/api/user",
        [](const HttpRequestPtr& req,
           std::function<void(const HttpResponsePtr&)>&& callback) {
            Json::Value json;
            json["name"] = "John Doe";
            json["age"] = 30;
            auto resp = HttpResponse::newHttpJsonResponse(json);
            callback(resp);
        },
        {Get});

    app().addListener("0.0.0.0", 8080).run();
}
```

```cpp
// POST request with JSON body parsing
#include <drogon/drogon.h>
using namespace drogon;

int main() {
    app().registerHandler("/api/data",
        [](const HttpRequestPtr& req,
           std::function<void(const HttpResponsePtr&)>&& callback) {
            auto json = req->getJsonObject();
            if (json) {
                auto resp = HttpResponse::newHttpJsonResponse(*json);
                callback(resp);
            } else {
                auto resp = HttpResponse::newHttpResponse();
                resp->setStatusCode(k400BadRequest);
                callback(resp);
            }
        },
        {Post});

    app().addListener("0.0.0.0", 8080).run();
}
```

```cpp
// Static file serving
#include <drogon/drogon.h>
using namespace drogon;

int main() {
    // Serve static files from ./public directory
    app().setStaticFilesPath("./public");
    app().addListener("0.0.0.0", 8080).run();
}
```

```cpp
// WebSocket handler
#include <drogon/drogon.h>
using namespace drogon;

int main() {
    app().registerWebSocketController("/ws", []() {
        return std::make_shared<WebSocketController>();
    });

    app().addListener("0.0.0.0", 8080).run();
}
```

```cpp
// Database integration with ORM
#include <drogon/drogon.h>
#include <drogon/orm/DbClient.h>
using namespace drogon;

int main() {
    // Configure database
    app().createDbClient("postgres", "localhost", 5432, "mydb", "user", "pass", 10);

    app().registerHandler("/users",
        [](const HttpRequestPtr& req,
           std::function<void(const HttpResponsePtr&)>&& callback) {
            auto db = app().getDbClient();
            db->execSqlAsync("SELECT * FROM users",
                [callback](const orm::Result& result) {
                    Json::Value users(Json::arrayValue);
                    for (auto& row : result) {
                        Json::Value user;
                        user["id"] = row["id"].as<int>();
                        user["name"] = row["name"].as<std::string>();
                        users.append(user);
                    }
                    auto resp = HttpResponse::newHttpJsonResponse(users);
                    callback(resp);
                },
                [callback](const orm::DrogonDbException& e) {
                    auto resp = HttpResponse::newHttpResponse();
                    resp->setStatusCode(k500InternalServerError);
                    callback(resp);
                });
        },
        {Get});

    app().addListener("0.0.0.0", 8080).run();
}
```