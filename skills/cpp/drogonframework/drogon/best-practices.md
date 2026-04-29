# Best Practices

```cpp
// Use dependency injection for testable code
class UserService {
public:
    virtual ~UserService() = default;
    virtual void getUsers(std::function<void(const Json::Value&)> callback) = 0;
};

class UserController {
    std::shared_ptr<UserService> userService;
public:
    explicit UserController(std::shared_ptr<UserService> service)
        : userService(std::move(service)) {}
    
    void handleGetUsers(const HttpRequestPtr& req,
                        std::function<void(const HttpResponsePtr&)>&& callback) {
        userService->getUsers([callback](const Json::Value& users) {
            auto resp = HttpResponse::newHttpJsonResponse(users);
            callback(resp);
        });
    }
};
```

```cpp
// Implement proper error handling middleware
class ErrorHandler {
public:
    static void handle(const HttpRequestPtr& req,
                       std::function<void(const HttpResponsePtr&)>&& callback,
                       const std::exception& e) {
        LOG_ERROR << "Error processing request: " << e.what();
        auto resp = HttpResponse::newHttpResponse();
        resp->setStatusCode(k500InternalServerError);
        resp->setBody("Internal server error");
        callback(resp);
    }
};

// Register as global error handler
app().setExceptionHandler(ErrorHandler::handle);
```

```cpp
// Use connection pooling for database operations
app().createDbClient("postgres", "localhost", 5432, "mydb", "user", "pass", 20); // Pool size 20

// Reuse connections across requests
auto db = app().getDbClient();
db->execSqlAsync("SELECT * FROM users WHERE id = $1",
    [](const orm::Result& result) {
        // Handle result
    },
    [](const orm::DrogonDbException& e) {
        // Handle error
    },
    1); // Parameter binding
```

```cpp
// Implement request validation
bool validateUserInput(const Json::Value& json) {
    if (!json.isMember("name") || !json["name"].isString()) return false;
    if (!json.isMember("age") || !json["age"].isInt()) return false;
    if (json["age"].asInt() < 0 || json["age"].asInt() > 150) return false;
    return true;
}

app().registerHandler("/api/user",
    [](const HttpRequestPtr& req,
       std::function<void(const HttpResponsePtr&)>&& callback) {
        auto json = req->getJsonObject();
        if (!json || !validateUserInput(*json)) {
            auto resp = HttpResponse::newHttpResponse();
            resp->setStatusCode(k400BadRequest);
            resp->setBody("Invalid input");
            callback(resp);
            return;
        }
        // Process valid input
    },
    {Post});
```