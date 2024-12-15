package hl4u

import (
	"bufio"
	"bytes"
	"fmt"
	"go-crawl/internal"
	"io"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/PuerkitoBio/goquery"
)

type safeSingerURLs struct {
	mx              sync.Mutex
	singerURLs      map[string]bool
	unProcessedURLs map[string]bool
}

func crawlSingers() {

	log.Println("Crawl Top Level Singers")

	safeURLs := safeSingerURLs{
		singerURLs:      make(map[string]bool),
		unProcessedURLs: make(map[string]bool),
	}

	var wg sync.WaitGroup

	startPage := safeURLs.initSingerURLs()

	if startPage == 100 {
		log.Println("All pages have been crawled")
		return
	} else {
		// start from the next page
		startPage++
		log.Println("Starting from page", startPage)
	}

	// start from the base url and crawl all the pages
	rootUrl := internal.Hl4uBaseURl + "/index.php?page="
	// there are 100 pages in total
	var endPage = 100
	for i := startPage; i <= endPage; i++ {
		time.Sleep(2 * time.Second)
		url := rootUrl + fmt.Sprintf("%d", i)
		log.Println("Processing page", url)
		wg.Add(1)
		go safeURLs.parseSingerPage(url, &wg)
	}

	wg.Wait()
	log.Println("Done crawling all pages")
	log.Println("Total singer urls", len(safeURLs.singerURLs))
	log.Println("writing to file")

	safeURLs.writeToFile(&endPage)
	log.Println("done writing to file")

	log.Println("crawl unprocessed urls")
	safeURLs.initUnprocessedURLs()
	for k, _ := range safeURLs.unProcessedURLs {
		wg.Add(1)
		log.Println("Processing unprocessed url", k)
		go safeURLs.parseSingerPage(k, &wg)
	}

	wg.Wait()

	log.Println("Done crawling unprocessed urls")
	log.Println("Total unprocessed singer urls", len(safeURLs.unProcessedURLs))
	log.Println("writing unprocessed urls to file")
	safeURLs.writeToFile(nil)
	log.Println("done writing unprocessed urls to file")

	fmt.Println("done crawling all singer urls")
}

func (ss *safeSingerURLs) writeToFile(endPage *int) {
	var fName string
	if endPage == nil {
		fName = internal.UnprocessedSingers
	} else {
		fName = internal.CrawledSingers
	}

	fh, err := os.Create(fName)
	if err != nil {
		log.Printf("error creating %s file: %v", fName, err.Error())
		// something went wrong, so return and try again
		return
	}

	defer fh.Close()

	if endPage != nil {
		_, err = fh.WriteString("last_page=" + strconv.Itoa(*endPage))
		if err != nil {
			log.Printf("error writing to file: %v", err.Error())
			// something went wrong, so return and try again
			return
		}
	}

	for k, _ := range ss.singerURLs {
		_, err := fh.WriteString("\n" + k)
		if err != nil {
			log.Printf("error writing to file: %v", err.Error())
			return
		}
	}
}

func (ss *safeSingerURLs) parseSingerPage(url string, wg *sync.WaitGroup) {

	defer wg.Done()

	req, err := http.NewRequest(http.MethodGet, url, nil)
	if err != nil {
		log.Printf("client: could not create request: %s\n", err)
		ss.mx.Lock()
		ss.unProcessedURLs[url] = true
		ss.mx.Unlock()
		return
	}

	req.Header.Set("Content-Type", "text/html")
	client := http.Client{
		Timeout: 30 * time.Second,
	}

	resp, err := client.Do(req)

	if err != nil {
		log.Printf("Error fetching url %s", url)
		// ignore this url. it needs to be crawled again
		ss.mx.Lock()
		ss.unProcessedURLs[url] = true
		ss.mx.Unlock()
		return
	}

	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		resp.Body.Close()
		log.Printf("error fetching url %s with status code %d", url, resp.StatusCode)
		// ignore this url. it needs to be crawled again
		ss.mx.Lock()
		ss.unProcessedURLs[url] = true
		ss.mx.Unlock()
		return
	}

	resBody, err := io.ReadAll(resp.Body)

	singerPage, err := goquery.NewDocumentFromReader(bytes.NewReader(resBody))
	if err != nil {
		log.Printf("error parsing index page: %v", err.Error())
		// ignore this url. it needs to be crawled again
		ss.mx.Lock()
		ss.unProcessedURLs[url] = true
		ss.mx.Unlock()
		return
	}

	singerPage.Find("td.w25p.h150 a").Each(func(i int, s *goquery.Selection) {
		link, _ := s.Attr("href")
		singerURL := internal.Hl4uBaseURl + link

		ss.mx.Lock()
		if _, ok := ss.singerURLs[singerURL]; ok {
			log.Printf("singer url already processed %s", singerURL)
			ss.mx.Unlock()
			return
		} else {
			log.Printf("singer url added to process %s", singerURL)
			ss.singerURLs[singerURL] = true
		}
		ss.mx.Unlock()
	})

}

func (ss *safeSingerURLs) initUnprocessedURLs() {

	fp, err := os.Open(internal.UnprocessedSingers)
	if err != nil {
		log.Fatal(err)
	}
	defer fp.Close()

	scanner := bufio.NewScanner(fp)
	for scanner.Scan() {
		url := scanner.Text()
		ss.unProcessedURLs[url] = true
		log.Println("Unprocessed singer url", url)
	}
	if err := scanner.Err(); err != nil {
		log.Fatal(err)
	}
}

func (ss *safeSingerURLs) initSingerURLs() int {
	lastVisitedPageVal := 0

	sfp, err := os.Open(internal.CrawledSingers)
	if err != nil {
		log.Fatal(err)
	}
	defer sfp.Close()

	scanner := bufio.NewScanner(sfp)

	scanner.Scan()
	lastPage := scanner.Text()
	log.Println("Last visited page", lastPage)

	if strings.HasPrefix(lastPage, "last_page") {
		lastPage = strings.Split(lastPage, "=")[1]
		lastVisitedPageVal, err = strconv.Atoi(lastPage)
		if err != nil {
			fmt.Printf("error parsing last page number")
			log.Fatal(err)
		}
	}
	// starting line 2 read the singer url file and populate singerURLs map
	for scanner.Scan() {
		alreadyScanned := scanner.Text()
		ss.singerURLs[alreadyScanned] = true
		log.Println("Already scanned singer url", alreadyScanned)
	}

	if err := scanner.Err(); err != nil {
		log.Fatal(err)
	}

	return lastVisitedPageVal
}
