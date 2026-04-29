package main

import (
	"context"
	"errors"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"
)

type User struct {
	ID   int    `json:"id"`
	Name string `json:"name" binding:"required,min=2,max=100"`
	Age  int    `json:"age"  binding:"gte=0,lte=150"`
}

var fakeDB = map[int]User{
	1: {ID: 1, Name: "Alice", Age: 30},
	2: {ID: 2, Name: "Bob", Age: 25},
}

func main() {
	gin.SetMode(gin.ReleaseMode)

	r := gin.New()
	r.Use(gin.Logger(), gin.CustomRecovery(func(c *gin.Context, err any) {
		c.AbortWithStatusJSON(500, gin.H{"error": "internal server error"})
	}))

	api := r.Group("/api/v1")
	{
		api.GET("/users", listUsers)
		api.GET("/users/:id", getUser)
		api.POST("/users", createUser)
	}

	srv := &http.Server{
		Addr:         ":8080",
		Handler:      r,
		ReadTimeout:  5 * time.Second,
		WriteTimeout: 10 * time.Second,
	}

	go func() {
		log.Printf("Server starting on :8080")
		if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
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
		log.Fatalf("shutdown: %v", err)
	}
}

func listUsers(c *gin.Context) {
	users := make([]User, 0, len(fakeDB))
	for _, u := range fakeDB {
		users = append(users, u)
	}
	c.JSON(http.StatusOK, gin.H{"data": users})
}

func getUser(c *gin.Context) {
	id := c.Param("id")
	// demo only: real code uses strconv.Atoi
	for _, u := range fakeDB {
		if u.ID == 1 && id == "1" || u.ID == 2 && id == "2" {
			c.JSON(http.StatusOK, gin.H{"data": u})
			return
		}
	}
	c.JSON(http.StatusNotFound, gin.H{"error": "user not found"})
}

func createUser(c *gin.Context) {
	var user User
	if err := c.ShouldBindJSON(&user); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	user.ID = len(fakeDB) + 1
	fakeDB[user.ID] = user
	c.JSON(http.StatusCreated, gin.H{"data": user})
}
