package main

import (
	"go-crawl/cmd/lyrics"
	"go-crawl/internal"
	"log"
	"os"
)

func main() {

	file, err := os.OpenFile(internal.LogFile, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0666)
	if err != nil {
		log.Fatal(err)
	}

	log.SetOutput(file)
	lyrics.SplitText()
}
