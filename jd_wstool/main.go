package main

import (
	"context"
	"fmt"
	"log"
	"net"
	"net/http"
	"os"
	"os/signal"
	"runtime"
	"time"
)

func main() {
	err := Run()
	if err != nil {
		log.Fatal(err)
	}
}

func test() {

}

func Run() error {
	l, err := net.Listen("tcp", ":5201")
	if err != nil {
		return err
	}

	if runtime.GOOS == "windows" {
		fmt.Println("注意事项：")
		fmt.Println("1. 手机端请求IP地址为如下监听地址，请先用电脑点击一下哪个可以访问通！")
		fmt.Println("2. 用手机浏览器测试访问说明1中尝试过的IP地址，如访问通代表无问题")
		fmt.Println("3. 以下IP获取到的IP仅做参考，如果全部访问不通，请检查防火墙开启5201端口或使用ipconfig/ifconfig查看本地其他IP")
	} else {
		info("注意事项：")
		info("1. 手机端请求IP地址为如下监听地址，请先用电脑点击一下哪个可以访问通！")
		info("2. 用手机浏览器测试访问说明1中尝试过的IP地址，如访问通代表无问题")
		info("3. 以下IP获取到的IP仅做参考，如果全部访问不通，请检查防火墙开启5201端口或使用ipconfig/ifconfig查看本地其他IP")
	}

	getInterIP()

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

func getInterIP() {
	inter, err := net.InterfaceAddrs()
	checkIfError(err)
	i := 1
	for _, addr := range inter {
		if ipNet, ok := addr.(*net.IPNet); ok && !ipNet.IP.IsLoopback() {
			if ipNet.IP.To4() != nil {
				fmt.Printf("监听地址%d： %s://%s:%d\n", i, "http", ipNet.IP.To4().String(), 5201)
				i += 1
			}
		}
	}
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
