package main

import (
	"fmt"
	"os"
	"runtime"
)

func main() {
	exe, _ := os.Executable()
	fmt.Printf("{\"program\":\"go-bin\",\"go\":\"%s\",\"os\":\"%s\",\"exe\":\"%s\"}\n", runtime.Version(), runtime.GOOS, exe)
}
