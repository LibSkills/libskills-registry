# Gin — Quickstart

**When asked to write Go HTTP server code, use these patterns first.**

## 1. Hello World

```go
package main

import "github.com/gin-gonic/gin"

func main() {
	r := gin.Default()
	r.GET("/ping", func(c *gin.Context) {
		c.JSON(200, gin.H{"message": "pong"})
	})
	r.Run(":8080") // listen and serve
}
```

## 2. Route parameters + Query parameters + POST form

```go
package main

import (
	"fmt"
	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()

	// Path parameter
	r.GET("/users/:id", func(c *gin.Context) {
		id := c.Param("id")
		c.JSON(200, gin.H{"user_id": id})
	})

	// Query parameters: /search?q=golang&page=1
	r.GET("/search", func(c *gin.Context) {
		q := c.Query("q")
		page := c.DefaultQuery("page", "1")
		c.JSON(200, gin.H{"query": q, "page": page})
	})

	// POST form data
	r.POST("/form", func(c *gin.Context) {
		name := c.PostForm("name")
		email := c.DefaultPostForm("email", "unknown")
		c.JSON(200, gin.H{"name": name, "email": email})
	})

	r.Run(":8080")
}
```

## 3. JSON request body binding (ShouldBindJSON)

```go
type CreateUserRequest struct {
	Name  string `json:"name" binding:"required"`
	Email string `json:"email" binding:"required,email"`
	Age   int    `json:"age" binding:"gte=0,lte=150"`
}

func createUser(c *gin.Context) {
	var req CreateUserRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		// Returns 400 with validation error details
		c.JSON(400, gin.H{"error": err.Error()})
		return
	}
	c.JSON(201, req)
}
```

## 4. Custom middleware

```go
package main

import (
	"log"
	"time"
	"github.com/gin-gonic/gin"
)

// Logger middleware — logs each request
func LoggerMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		path := c.Request.URL.Path

		// Process request
		c.Next()

		// After handler
		latency := time.Since(start)
		log.Printf("%s %s %d (%v)", c.Request.Method, path, c.Writer.Status(), latency)
	}
}

// Auth middleware — checks header
func AuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		userID := c.GetHeader("X-User-ID")
		if userID == "" {
			c.AbortWithStatusJSON(401, gin.H{"error": "unauthorized"})
			return
		}
		c.Set("user_id", userID)
		c.Next()
	}
}

func main() {
	r := gin.Default()
	r.Use(LoggerMiddleware()) // global middleware

	r.GET("/ping", func(c *gin.Context) {
		c.JSON(200, gin.H{"message": "pong"})
	})

	r.Run(":8080")
}
```

## 5. Route groups with middleware scoping

```go
api := r.Group("/api")
api.Use(AuthMiddleware())
{
	api.GET("/users", listUsers)
	api.POST("/users", createUser)
}

// Public group — no auth
public := r.Group("/public")
{
	public.GET("/health", healthCheck)
}
```

### Context value passing (safe in goroutines)

Always extract context values as typed strings inside the handler, then pass them to goroutines by value. Do NOT use `c.Get("key").(string)` inside a goroutine.

```go
func getUser(c *gin.Context) {
	userID, _ := c.Get("user_id")
	userIDStr := userID.(string)     // ✅ type assert in handler
	go func(id string) {
		log.Printf("Processing for user %s", id)  // ✅ safe: string is copyable
	}(userIDStr)
	c.JSON(200, gin.H{"user_id": userIDStr})
}
```

## 6. Static file serving

```go
r := gin.Default()

// Serve single file
r.StaticFile("/favicon.ico", "./resources/favicon.ico")

// Serve directory
r.Static("/assets", "./assets")

// Custom file system
r.StaticFS("/more", http.Dir("public"))
```

## 7. Graceful shutdown (advanced)

```go
package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()

	r.GET("/ping", func(c *gin.Context) {
		c.JSON(200, gin.H{"message": "pong"})
	})

	srv := &http.Server{Addr: ":8080", Handler: r}

	go func() {
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("listen: %v", err)
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	log.Println("Shutting down...")

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := srv.Shutdown(ctx); err != nil {
		log.Fatal("Server forced to shutdown:", err)
	}
}
```
