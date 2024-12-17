package lyrics

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"time"

	"go-crawl/internal"

	"github.com/PuerkitoBio/goquery"
)

type TrackLyrics struct {
	trackName   string
	lyricsText  string
	lyricsImage []byte
}

/*
open and read lyrics urls file
for each track, look at the set of urls
visit each url where you will find two elements:
one is a span with itewprop="text" that contains english text lyrics of the track
the second is an img with itemprop="image" that contains the image of the track as src
extract the text and image src and save them on disk

text lyrics are stored with filename as trackname.txt
at /Users/manojsaxena/data/lyrics/text directory

image is stored with filename as trackname.png
/Users/manojsaxena/data/lyrics/image directory
*/

func ScrapeLyrics() {
	readJSONToken(internal.TrackLyricsMapPath)
}

func readJSONToken(fileName string) {
	fileBytes, _ := os.ReadFile(fileName)

	trackURLs := make(map[string]map[string]bool)

	err := json.Unmarshal(fileBytes, &trackURLs)
	if err != nil {
		log.Printf("error unmarshalling json file %s\n", fileName)
		return
	}

	for track, urls := range trackURLs {
		ctr := 0
		for url, _ := range urls {
			go extractLyrics(track, url, ctr)
			time.Sleep(2 * time.Second)
			ctr++
		}
	}
}

func extractLyrics(track string, url string, ctr int) {

	lyricsObj := TrackLyrics{trackName: track}

	finalURL := internal.Hl4uBaseURl + url
	resp, err := http.Get(finalURL)
	if err != nil {
		log.Printf("error http get lyrics page for track - %s at URL %s\n", track, finalURL)
		return
	}
	defer func(Body io.ReadCloser) {
		err := Body.Close()
		if err != nil {
			log.Printf("error closing body for URL %s\n", finalURL)
			return
		}
	}(resp.Body)

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		log.Printf("error reading body for %s\n", finalURL)
		return
	}
	rawPage, err := goquery.NewDocumentFromReader(bytes.NewReader(respBody))
	if err != nil {
		log.Printf("error parsing body for %s\n", finalURL)
		return
	}
	mainSpan := rawPage.Find("span[itemprop='lyrics']")
	sel := mainSpan.Children()
	if sel.Length() == 0 {
		log.Printf("no lyrics found for track - %s at URL %s\n", track, finalURL)
		return
	}
	asText := ""
	sel.First().Each(func(i int, s *goquery.Selection) {
		asText += s.Text()
	})
	if asText == "" {
		log.Printf("no text lyrics found for track %s at URL %s\n", track, finalURL)
		return
	}

	lyricsObj.lyricsText = asText

	imgURL, _ := sel.Last().Attr("src")
	imgURL = internal.Hl4uBaseURl + imgURL
	if imgURL == "" {
		log.Printf("no image of lyrics found for track %s at URL %s\n", track, finalURL)
		return
	}

	// fetch image
	resp, err = http.Get(imgURL)
	if err != nil {
		log.Printf("error fetching image of lyrics for track %s at URL %s\n", track, finalURL)
		return
	}
	defer func(Body io.ReadCloser) {
		err := Body.Close()
		if err != nil {
			log.Printf("error closing body for URL %s\n", imgURL)
			return
		}
	}(resp.Body)
	lyricsImageBody, err := io.ReadAll(resp.Body)
	if err != nil {
		log.Printf("error reading image body for track %s at URL %s\n", track, imgURL)
		return
	}
	lyricsObj.lyricsImage = lyricsImageBody
	lyricsObj.saveLyrics(ctr)
}

func (tl *TrackLyrics) saveLyrics(ctr int) {
	lyricsTextPath := internal.LyricsTextPath + tl.trackName + fmt.Sprintf("_%d", ctr) + ".txt"
	lyricsImagePath := internal.LyricsImagePath + tl.trackName + fmt.Sprintf("_%d", ctr) + ".png"

	err := os.WriteFile(lyricsTextPath, []byte(tl.lyricsText), os.ModePerm)
	if err != nil {
		log.Printf("error saving lyrics text for track %s\n", tl.trackName)
		return
	}

	// save image
	err = os.WriteFile(lyricsImagePath, tl.lyricsImage, os.ModePerm)
	if err != nil {
		log.Printf("error saving lyrics image for track %s\n", tl.trackName)
		return
	}
}
