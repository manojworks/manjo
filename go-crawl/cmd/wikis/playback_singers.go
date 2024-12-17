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

func processPlaybackSingersPage() {

	outFile := internal.CrawledFilesPath + "wiki_payback_singers.csv"
	fo, err := os.Create(outFile)
	if err != nil {
		log.Printf("error creating file %s", outFile)
		panic(err)

	}
	fName := internal.CrawledFilesPath + "wiki_payback_singers.html"
	fh, err := os.Open(fName)
	if err != nil {
		log.Printf("error opening file %s", fName)
		panic(err)
	}

	doc, err := io.ReadAll(fh)
	if err != nil {
		log.Printf("error reading file %s", fName)
		panic(err)

	}
	singerPage, err := goquery.NewDocumentFromReader(bytes.NewReader(doc))
	if err != nil {
		log.Printf("error parsing index page: %v", err.Error())
		return

	}
	//<table class="wikitable sortable">
	//
	//	<tbody>
	//		<tr>
	//			<th>Years active 2018
	//			</th> <th>Name</th>
	//			<th>Language</th>
	//		</tr>
	//		<tr>
	//			<td>1998–present</td>
	//			<td><a href="/wiki/A._R._Reihana" title="A. R. Reihana">A. R. Reihana</a> </td>
	//			<td><a href="/wiki/Tamil_language" title="Tamil language">Tamil</a> </td>
	//		</tr>
	//	</tbody>
	//</table>

	singerPage.Find("table.wikitable").Each(func(i int, s *goquery.Selection) {
		s.Find("tbody").Each(func(i int, s *goquery.Selection) {
			s.Find("tr").Each(func(i int, s *goquery.Selection) {
				name := strings.TrimSpace(s.Find("td").First().Next().Text())
				if name == "" {
					return
				}
				yearPart := strings.TrimSuffix(s.Find("td").First().Text(), "\n")
				yearRange := strings.Split(yearPart, "–")
				startYear := ""
				endYear := ""
				switch len(yearRange) {
				case 2:
					startYear = yearRange[0]
					endYear = yearRange[1]
				case 1:
					startYear = yearRange[0]
					endYear = ""
				default:
					startYear = ""
					endYear = ""
				}
				_, err := fo.WriteString(fmt.Sprintf("%s,%s,%s\n", name, strings.TrimSpace(startYear), strings.TrimSpace(endYear)))
				if err != nil {
					return
				}
				println(strings.TrimSpace(startYear), strings.TrimSpace(endYear), name)
			})
		})
	})
	err = fo.Close()
	if err != nil {
		return
	}
	err = fh.Close()
	if err != nil {
		return
	}
}

func fetchAndSavePlaybackSingers() {

	singersPage, err := fetchPlaybackSingers()
	if err != nil {
		return
	}
	err = savePlaybackSingerDocument(singersPage)
	if err != nil {
		return
	}
	log.Println("Process Playback Singers")

}

func savePlaybackSingerDocument(pageBody []byte) error {

	fName := "wiki_payback_singers.html"
	fh, err := os.Create(internal.CrawledFilesPath + fName)
	if err != nil {
		fmt.Println("Error creating file", fName)
		panic(err)
	}
	defer func(fh *os.File) {
		err := fh.Close()
		if err != nil {
			log.Printf("error closing file: %v", err.Error())
		}
	}(fh)
	_, err = fh.Write(pageBody)
	if err != nil {
		return err
	}
	return nil
}

func fetchPlaybackSingers() ([]byte, error) {

	log.Println("Fetch Playback Singers from Wikipedia")

	log.Printf("crawling page with url %s", internal.PlaybackSingersURl)
	req, err := http.NewRequest(http.MethodGet, internal.PlaybackSingersURl, nil)
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
		log.Printf("error fetching url %s", internal.PlaybackSingersURl)
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
		log.Printf("error fetching url %s with status code %d", internal.PlaybackSingersURl, resp.StatusCode)
		return nil, fmt.Errorf("error fetching url %s with status code %d", internal.PlaybackSingersURl, resp.StatusCode)
	}

	resBody, err := io.ReadAll(resp.Body)

	if err != nil {
		log.Printf("error getting sinegr page: %v", err.Error())
		return nil, err
	}

	log.Printf("crawled page with url %s", internal.PlaybackSingersURl)

	return resBody, nil
}
