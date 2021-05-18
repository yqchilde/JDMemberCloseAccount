package main

import (
	"context"
	"fmt"
	"log"
	"net"
	"net/http"
	"os"
	"os/signal"
	"strings"
	"time"
)

func main() {

	err := Run()
	if err != nil {
		log.Fatal(err)
	}
}

func Run() error {
	l, err := net.Listen("tcp", ":5201")
	if err != nil {
		return err
	}
	fmt.Printf("listening on %s://%s:%d\n", "http", getInterIP(), 5201)

	cs := NewChatServer()
	s := &http.Server{
		Handler:      cs,
		ReadTimeout:  time.Second * 30,
		WriteTimeout: time.Second * 30,
	}
	channelErr := make(chan error, 1)
	go func() {
		channelErr <- s.Serve(l)
	}()

	signals := make(chan os.Signal, 1)
	signal.Notify(signals, os.Interrupt)
	select {
	case err := <-channelErr:
		log.Printf("failed to serve: %v", err)
	case sig := <-signals:
		log.Printf("terminating: %v", sig)
	}

	ctx, cancel := context.WithTimeout(context.Background(), time.Second*60)
	defer cancel()

	return s.Shutdown(ctx)
}

func getInterIP() string {
	inter, _ := net.InterfaceAddrs()
	for i := range inter {
		if strings.HasPrefix(inter[i].String(), "192.168") {
			return strings.Split(inter[i].String(), "/")[0]
		}
	}

	return ""
}
