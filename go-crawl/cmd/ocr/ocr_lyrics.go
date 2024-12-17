package ocr

import (
	"bufio"
	"go-crawl/internal"
	"log"
	"os"
	"strings"
	"time"

	"github.com/otiai10/gosseract/v2"
)

func ProcessImageFiles() {

	imageFiles := filesToProcess()

	for _, file := range imageFiles {
		log.Println("Processing file " + file)
		doOCR(file)
		time.Sleep(1 * time.Second)
	}
}

func filesToProcess() []string {

	imageFiles, err := os.ReadDir(internal.SourceOCRImageDir)
	if err != nil {
		log.Panic(err)
	}
	badImages := badImageFiles()

	var files []string
	for _, file := range imageFiles {
		cFileName := compressedFilename(file.Name())
		_, err = os.Stat(internal.DestOCRMixedTextDir + cFileName + ".txt")
		if err == nil {
			log.Println("Skipping already processed file " + file.Name())
			continue
		}
		if (*badImages)[cFileName] {
			log.Println("Skipping bad file " + file.Name())
			continue
		}
		files = append(files, file.Name())
		if len(files) == 1000 {
			log.Println("identified 1000 files to process")
			break
		}
	}
	return files

}

func badImageFiles() *map[string]bool {

	errorText := "Error in reading text for file"

	fl, err := os.Open(internal.LogFile)
	if err != nil {
		log.Panic(err)
	}
	defer func(fl *os.File) {
		err := fl.Close()
		if err != nil {
			log.Println(err)
		}
	}(fl)

	scanner := bufio.NewScanner(fl)
	files := make(map[string]bool)
	for scanner.Scan() {
		line := scanner.Text()
		if strings.Contains(line, errorText) {
			line = strings.Split(line, errorText)[1]
			line = strings.Trim(line, " ")
			line = strings.Split(line, ".png")[0]
			line = compressedFilename(line)
			files[line] = true
		}
	}
	return &files
}

func doOCR(fName string) {

	client := gosseract.NewClient()
	defer func(client *gosseract.Client) {
		err := client.Close()
		if err != nil {
			log.Println(err)
		}
	}(client)
	// for two column as in our case
	err := client.SetPageSegMode(gosseract.PSM_AUTO)
	// detect both english and hindi words
	err = client.SetLanguage("eng+hin")
	err = client.SetImage(internal.SourceOCRImageDir + fName)
	if err != nil {
		log.Println(err)
		log.Println("Error in setting image for file " + fName)
		return
	}
	mixedText, err := client.Text()
	if err != nil {
		log.Println(err)
		log.Println("Error in reading text for file " + fName)
		return
	}

	err = os.WriteFile(internal.DestOCRMixedTextDir+compressedFilename(fName)+".txt", []byte(mixedText), 0644)
	if err != nil {
		log.Println(err)
		log.Println("Error in writing text for file " + fName)
		return
	}
}

func compressedFilename(fName string) string {

	fName = strings.ReplaceAll(fName, " ", "_")
	fName = strings.ReplaceAll(fName, "'", "")
	fName = strings.ReplaceAll(fName, "(", "")
	fName = strings.ReplaceAll(fName, ")", "")
	fName = strings.ReplaceAll(fName, ",", "")
	dotIndex := strings.LastIndex(fName, ".")
	if dotIndex == -1 {
		return fName
	} else {
		return fName[:dotIndex]
	}

}
