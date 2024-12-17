package wikis

import (
	"bytes"
	"fmt"
	"go-crawl/internal"
	"io"
	"log"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/PuerkitoBio/goquery"
)

func processComposersPage() {

	outFile := internal.CrawledFilesPath + "wiki_composers.csv"
	fo, err := os.Create(outFile)
	if err != nil {
		log.Printf("error creating file %s", outFile)
		panic(err)

	}

	doc, err := fetchComposers()
	if err != nil {
		log.Printf("error fetching composers")
		panic(err)

	}
	composerPage, err := goquery.NewDocumentFromReader(bytes.NewReader(doc))
	if err != nil {
		log.Printf("error parsing composer page: %v", err.Error())
		return
	}

	//<div class="div-col" style="column-width: 30em;">
	//<ul><li><a href="/wiki/Annamacharya" title="Annamacharya">Annamacharya</a></li>
	//<li><a href="/wiki/Chembai_Vaidyanatha_Bhagavatar" class="mw-redirect" title="Chembai Vaidyanatha Bhagavatar">Chembai Vaidyanatha Bhagavatar</a></li>
	//<li><a href="/wiki/Ilayaraja" class="mw-redirect" title="Ilayaraja">Ilayaraja</a></li>
	// ...
	//</ul>
	//</div>

	composerPage.Find("div.div-col").Each(func(i int, s *goquery.Selection) {
		s.Find("ul li").Each(func(i int, s *goquery.Selection) {
			name := strings.TrimSpace(s.Find("a").Text())
			_, err := fo.WriteString(fmt.Sprintf("%s\n", name))
			if err != nil {
				return
			}
			fmt.Println(name)
		})
	})
	err = fo.Close()
	if err != nil {
		return
	}
}

func fetchComposers() ([]byte, error) {

	log.Println("Fetch Composers from Wikipedia")

	log.Printf("crawling page with url %s", internal.ComposersURl)
	req, err := http.NewRequest(http.MethodGet, internal.ComposersURl, nil)
	if err != nil {
		log.Printf("client: could not create request: %s\n", err)
		return nil, err
	}

	req.Header.Set("Content-Type", "text/html")
	client := http.Client{
		Timeout: 30 * time.Second,
	}

	resp, err := client.Do(req)

	if err != nil {
		log.Printf("error fetching url %s", internal.ComposersURl)
		return nil, err
	}

	defer func(Body io.ReadCloser) {
		err := Body.Close()
		if err != nil {
			log.Printf("error closing response body: %v", err.Error())
		}
	}(resp.Body)

	if resp.StatusCode != http.StatusOK {
		err := resp.Body.Close()
		if err != nil {
			return nil, err
		}
		log.Printf("error fetching url %s with status code %d", internal.ComposersURl, resp.StatusCode)
		return nil, fmt.Errorf("error fetching url %s with status code %d", internal.ComposersURl, resp.StatusCode)
	}

	resBody, err := io.ReadAll(resp.Body)

	if err != nil {
		log.Printf("error getting sinegr page: %v", err.Error())
		return nil, err
	}

	log.Printf("crawled page with url %s", internal.ComposersURl)

	return resBody, nil
}
