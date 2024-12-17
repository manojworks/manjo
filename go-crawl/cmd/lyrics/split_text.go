package lyrics

import (
	"bufio"
	"go-crawl/internal"
	"log"
	"os"
	"regexp"
	"strings"
	"sync"
)

// Devanagari Unicode range
var pattern, _ = regexp.Compile("[\u0900-\u097f]+")

func SplitText() {
	wg := sync.WaitGroup{}
	ctr := 0
	files, _ := os.ReadDir(internal.MixedTextDir)
	for _, file := range files {
		log.Println("Processing file ", file.Name())
		wg.Add(1)
		go readText(file.Name(), &wg)
		ctr++
		if ctr == 10 {
			break
		}
	}
	wg.Wait()

}

func readText(fName string, wg *sync.WaitGroup) {
	fp, err := os.Open(internal.MixedTextDir + fName)
	if err != nil {
		log.Println(err)
		log.Println("Error opening file ", fName)
		wg.Done()
		return
	}

	defer func(fp *os.File) {
		err := fp.Close()
		if err != nil {
			log.Println(err)
			log.Println("Error closing file ", fName)
			wg.Done()
			return
		}
	}(fp)

	baseName := strings.Split(fName, ".")[0]
	hindiFp, err := os.Create(internal.HindiTextDir + baseName + "_hin" + ".txt")
	if err != nil {
		log.Println(err)
		log.Println("Error creating file ", internal.HindiTextDir+baseName+"_hin"+".txt")
		wg.Done()
		return
	}
	defer func(fp *os.File) {
		err := fp.Close()
		if err != nil {
			log.Println(err)
			log.Println("Error closing file ", internal.HindiTextDir+baseName+"_hin"+".txt")
			wg.Done()
			return
		}
	}(hindiFp)

	englishFp, err := os.Create(internal.EnglishTextDir + baseName + "_eng" + ".txt")
	if err != nil {
		log.Println(err)
		log.Println("Error creating file ", internal.EnglishTextDir+baseName+"_eng"+".txt")
		wg.Done()
		return
	}
	defer func(fp *os.File) {
		err := fp.Close()
		if err != nil {
			log.Println(err)
			log.Println("Error closing file ", internal.EnglishTextDir+baseName+"_eng"+".txt")
			wg.Done()
			return
		}
	}(englishFp)
	var englishPart string
	scanner := bufio.NewScanner(fp)

	for scanner.Scan() {
		ln := scanner.Text()
		index := pattern.FindStringIndex(ln)
		if index == nil {
			log.Printf("hindi part not found in file %s for line %s\n", fName, ln)
			englishPart = ln
		} else {
			englishPart = ln[:index[0]]

			hindiPart := ln[index[0]:]
			if len(hindiPart) > 0 {
				_, err = hindiFp.WriteString(hindiPart + "\n")
				//TODO: Handle err
			} else {
				log.Printf("hindi part not found in file %s for line %s\n", fName, ln)
			}
		}
		if len(englishPart) > 0 {
			//TODO: Handle err
			_, err = englishFp.WriteString(englishPart + "\n")
		} else {
			log.Printf("english part not found in file %s for line %s\n", fName, ln)
		}
	}
	wg.Done()
}
