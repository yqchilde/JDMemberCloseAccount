package main

import (
	"context"
	"fmt"
	"log"
	"net"
	"net/http"
	"os"
	"os/signal"
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

	info("注意事项：")
	info("1. 手机端请求IP地址为如下监听地址")
	info("2. 先用手机浏览器测试访问，如连接通代表无问题，访问不通请检查防火墙开启5201端口或使用ipconfig/ifconfig查看本地其他IP")
	fmt.Printf("监听地址： %s://%s:%d\n", "http", getInterIP(), 5201)

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
	inter, err := net.InterfaceAddrs()
	checkIfError(err)
	for i := range inter {
		if ipNet, ok := inter[i].(*net.IPNet); ok && !ipNet.IP.IsLoopback() {
			if ipNet.IP.To4() != nil {
				return ipNet.IP.To4().String()
			}
		}
	}

	return ""
}

// info should be used to describe the example commands that are about to run.
func info(format string, args ...interface{}) {
	fmt.Printf("\033[1;36m%s\033[0m\n", fmt.Sprintf(format, args...))
}

// checkIfError should be used to naively panics if an error is not nil.
func checkIfError(err error) {
	if err == nil {
		return
	}

	fmt.Printf("\x1b[31;1m%s\x1b[0m\n", fmt.Sprintf("error: %s", err))
	os.Exit(1)
}
