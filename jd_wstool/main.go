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
	err := start()
	if err != nil {
		log.Fatal(err)
	}
}

func start() error {
	if runtime.GOOS == "windows" {
		fmt.Println("注意事项：")
		fmt.Println("1. 手机端请求IP地址为监听地址，请先测试是否可以访问通")
		fmt.Println("2. 用手机浏览器测试访问说明1中尝试过的IP地址，如访问通代表无问题")
		fmt.Println("3. 以下IP获取到的IP仅做参考，如果全部访问不通，请检查防火墙是否开启如下端口或使用ipconfig/ifconfig查看本地其他IP")
		fmt.Println("4. 记得更改手机端的请求地址，并授权软件短信权限和验证码获取权限")
	} else {
		info("注意事项：")
		info("1. 手机端请求IP地址为监听地址，请先测试是否可以访问通")
		info("2. 用手机浏览器测试访问说明1中尝试过的IP地址，如访问通代表无问题")
		info("3. 以下IP获取到的IP仅做参考，如果全部访问不通，请检查防火墙是否开启如下端口或使用ipconfig/ifconfig查看本地其他IP")
		info("4. 记得更改手机端的请求地址，并授权软件短信权限和验证码获取权限")
	}

	args := os.Args[1:]
	if len(args) == 0 {
		args = append(args, "5201")
	}
	getInterIP(args)

	cs := NewChatServer()
	s := &http.Server{
		Handler:      cs,
		ReadTimeout:  time.Second * 30,
		WriteTimeout: time.Second * 30,
	}
	channelErr := make(chan error, len(args))
	for _, arg := range args {
		l, err := net.Listen("tcp", fmt.Sprintf(":%s", arg))
		if err != nil {
			return err
		}

		go func() {
			channelErr <- s.Serve(l)
		}()
	}

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

func getInterIP(ports []string) {
	inter, err := net.InterfaceAddrs()
	checkIfError(err)
	i := 1
	for _, addr := range inter {
		if ipNet, ok := addr.(*net.IPNet); ok && !ipNet.IP.IsLoopback() {
			if ipNet.IP.To4() != nil {
				for _, port := range ports {
					fmt.Printf("监听地址%d： %s://%s:%s/publish?smsCode=123456\n", i, "http", ipNet.IP.To4().String(), port)
					i++
				}
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
