package hl4u

import (
	"bufio"
	"bytes"
	"fmt"
	"go-crawl/internal"
	"io"
	"log"
	"math/rand"
	"net/http"
	"os"
	"regexp"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/PuerkitoBio/goquery"
)

var exp = regexp.MustCompile(`/singer/`)

type safeSingerPages struct {
	mx          sync.Mutex
	singerPages map[string]bool
	fp          *os.File
}

func fetchAllSingerPages() {

	log.Println("Fetch Singer Pages")

	safePages := safeSingerPages{
		singerPages: make(map[string]bool),
	}

	safePages.initSingerPageFetch()

	log.Printf("open singer file %s", internal.CrawledSingers)
	fh, err := os.Open(internal.CrawledSingers)
	if err != nil {
		log.Printf("error opening file %s", internal.CrawledSingers)
		panic(err)
	}
	defer fh.Close()

	scanner := bufio.NewScanner(fh)
	// skip the first line this is page_count
	scanner.Scan()

	wg := sync.WaitGroup{}
	defer wg.Done()

	for scanner.Scan() {
		time.Sleep(1 * time.Second)
		log.Printf("read singer url %s", scanner.Text())
		wg.Add(1)
		go safePages.fetchSingerPages(scanner.Text())
	}

	if err := scanner.Err(); err != nil {
		log.Fatal(err)
	}
	wg.Wait()

	log.Printf("processed all singers")
}

func (ss *safeSingerPages) fetchSingerPages(url string) {

	var wg sync.WaitGroup

	// fetch the first page
	r := exp.Split(url, 2)
	singerBaseUrl := strings.Join(r, "/")
	pageNumber := 1
	singerFirstUrl := singerBaseUrl + fmt.Sprintf("?page=%d", pageNumber)
	log.Printf("first page url %s: ", singerFirstUrl)
	saveFirstPage := true
	ss.mx.Lock()
	if _, ok := ss.singerPages[singerFirstUrl]; ok {
		log.Printf("singer url already processed %s", singerFirstUrl)
		saveFirstPage = false
	}
	ss.mx.Unlock()

	//  allow for 20 concurrent requests
	var tokens = make(chan struct{}, 20)
	doc := make(chan []byte)
	wg.Add(1)
	tokens <- struct{}{}
	go getPage(singerFirstUrl, doc)
	<-tokens

	firstPage := <-doc
	if len(firstPage) == 0 {
		log.Printf("error fetching first page %s", singerFirstUrl)
		// ignore this url. it needs to be crawled again
		return
	}
	// from the first page extract singer name and number of pages
	// then save the file
	singerName, pageCount := ss.processFirstPage(singerFirstUrl, firstPage, saveFirstPage)
	if singerName == nil || pageCount == nil {
		log.Printf("error processing first page %s", singerFirstUrl)
		// ignore this url. it needs to be crawled again
		return
	}
	close(doc)

	log.Printf("first page processing completed")

	doc = make(chan []byte, *pageCount)

	defer wg.Done()

	wg.Add(*pageCount - 1)
	for pageNumber = 2; pageNumber <= *pageCount; pageNumber++ {
		// sleep randomly between 1 and 5 seconds
		time.Sleep(time.Duration(1+rand.Intn(5)) * time.Second)
		singerUrl := singerBaseUrl + fmt.Sprintf("?page=%d", pageNumber)
		log.Printf("next page url %s ", singerUrl)
		ss.mx.Lock()
		if _, ok := ss.singerPages[singerUrl]; ok {
			log.Printf("singer page url already processed %s", singerUrl)
			ss.mx.Unlock()
			continue
		}
		ss.mx.Unlock()

		tokens <- struct{}{}
		go getPage(singerUrl, doc)

		page := <-doc
		if len(page) == 0 {
			log.Printf("error fetching page %s", singerUrl)
			// ignore this url. it needs to be crawled again
			return
		}
		err := saveSingerDocument(*singerName, pageNumber, page)
		if err != nil {
			log.Printf("error saving page %s", singerUrl)
			log.Printf("%v", err)
			// ignore this url. it needs to be crawled again
			return
		}
		ss.mx.Lock()
		err = ss.updateListOfSingerPages(ss.fp, singerUrl)
		if err != nil {
			log.Printf("error updating singer pages %s", singerUrl)
			log.Printf("%v", err)
			return
		}
		ss.singerPages[singerUrl] = true
		ss.mx.Unlock()
		<-tokens
	}
	wg.Wait()
	//TODO: when to close the file
	//ss.fp.Close()

	log.Printf("processed all pages for singer %s", *singerName)
}

func (ss *safeSingerPages) processFirstPage(singerFirstUrl string, pageBody []byte, saveFirstPage bool) (*string, *int) {

	var singerName string
	var pageCount int

	log.Printf("process first page %s", singerFirstUrl)
	firstPage, err := goquery.NewDocumentFromReader(bytes.NewReader(pageBody))
	if err != nil {
		log.Printf("error parsing first page: %v", err.Error())
		// ignore this url. it needs to be crawled again
		return nil, nil
	}

	firstPage.Find("title").Each(func(i int, s *goquery.Selection) {
		title := s.Text()
		// title format is <title>Asha Bhosle - 7650+ songs sung by the singer - Page 12 of 767</title>
		singerName = strings.TrimSpace(title[:strings.Index(title, "-")])
		pageCount, err = strconv.Atoi(strings.TrimSpace(title[strings.LastIndex(title, " "):]))
		if err != nil {
			log.Printf("error parsing page count: %v", err.Error())
			// ignore this url. it needs to be crawled again
			return
		}
		log.Printf("*** processed first page with title %s and singer %s and page count %d", title, singerName, pageCount)
	})

	if saveFirstPage {
		err = saveSingerDocument(singerName, 1, pageBody)
		if err != nil {
			log.Printf("error saving first page %s", singerName)
			log.Printf("%v", err)
			// ignore this url. it needs to be crawled again
			return nil, nil
		}
		log.Printf("saved first singer page for singer %s", singerName)
	}
	ss.mx.Lock()
	log.Printf("update singer pages %s", singerFirstUrl)
	err = ss.updateListOfSingerPages(ss.fp, singerFirstUrl)
	if err != nil {
		log.Printf("error updating singer pages %s", singerFirstUrl)
		return nil, nil
	}
	ss.singerPages[singerFirstUrl] = true
	ss.mx.Unlock()

	return &singerName, &pageCount
}

func saveSingerDocument(singerName string, pageNumber int, pageBody []byte) error {

	fName := fmt.Sprintf("%s_%d.html", singerName, pageNumber)
	fh, err := os.Create(internal.CrawledFilesPath + fName)
	if err != nil {
		fmt.Println("Error creating file", fName)
		panic(err)
	}
	defer fh.Close()
	_, err = fh.Write(pageBody)
	if err != nil {
		return err
	}
	return nil
}

func (ss *safeSingerPages) updateListOfSingerPages(fp *os.File, pageURL string) error {
	_, err := fp.WriteString(pageURL + "\n")
	if err != nil {
		log.Printf("error writing to file: %v", err.Error())
		return err
	}
	return nil
}

func getPage(url string, out chan []byte) {

	log.Printf("crawling page with url %s", url)
	req, err := http.NewRequest(http.MethodGet, url, nil)
	if err != nil {
		log.Printf("client: could not create request: %s\n", err)
		return
	}

	req.Header.Set("Content-Type", "text/html")
	client := http.Client{
		Timeout: 30 * time.Second,
	}

	resp, err := client.Do(req)

	if err != nil {
		log.Printf("error fetching url %s", url)
		return
	}

	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		resp.Body.Close()
		log.Printf("error fetching url %s with status code %d", url, resp.StatusCode)
		return
	}

	resBody, err := io.ReadAll(resp.Body)

	if err != nil {
		log.Printf("error getting sinegr page: %v", err.Error())
		return
	}

	log.Printf("crawled page with url %s", url)
	out <- resBody
}

func (ss *safeSingerPages) initSingerPageFetch() {
	log.Printf("open singer pages file %s", internal.CrawledSingerPages)
	fp, err := os.OpenFile(internal.CrawledSingerPages, os.O_RDWR|os.O_APPEND, 0644)
	if err != nil {
		log.Printf("error opening file %s", internal.CrawledSingerPages)
		panic(err)
	}

	scanner := bufio.NewScanner(fp)

	for scanner.Scan() {
		ss.singerPages[scanner.Text()] = true
	}

	ss.fp = fp
	if err := scanner.Err(); err != nil {
		log.Fatal(err)
	}
}
