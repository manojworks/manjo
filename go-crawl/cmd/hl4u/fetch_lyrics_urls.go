package hl4u

import (
	"bytes"
	"encoding/json"
	"errors"
	"go-crawl/internal"
	"log"
	"os"
	"strings"

	"github.com/PuerkitoBio/goquery"
)

var lyricsFileMap = make(map[string]map[string]bool)

func FetchLyricsURLs() {

	fetchBasePages()
}

func fetchBasePages() {

	fp, err := os.ReadDir(internal.Hl4uPath)
	if err != nil {
		os.Exit(-1)
	}

	for _, f := range fp {
		rawFile := internal.Hl4uPath + f.Name()

		rf, err := os.OpenFile(rawFile, os.O_RDONLY, 0666)
		if err != nil {
			log.Println(err)
			log.Println("fetch lyrics error " + rawFile)
		}
		err = scrapeLyricsLinks(rf)
		if errors.Is(err, errors.New(internal.ReadFileError)) {
			log.Println(err)
			log.Println("fetch lyrics error " + rawFile)
		}
	}

	lyricsURL, err := json.Marshal(lyricsFileMap)
	if err != nil {
		os.Exit(-1)
	}

	err = os.WriteFile(internal.TrackLyricsMapPath, lyricsURL, os.ModePerm)
	if err != nil {
		os.Exit(-1)
	}
}

func scrapeLyricsLinks(rf *os.File) error {

	rawText := make([]byte, 1000000)
	n, err := rf.Read(rawText)
	if err != nil {
		return errors.New(internal.ReadFileError)
	}
	if n == 0 {
		return errors.New(internal.ReadFileError)
	}
	rawPage, err := goquery.NewDocumentFromReader(bytes.NewReader(rawText))
	if err != nil {
		return errors.New(internal.ReadFileError)
	}

	/*
		 from the table extract href and span
		<table class="b1 w760 bgff pad2 allef">
		 <tr>
		   <td rowspan="2" class="w105 vatop"><a href="/song/aap_ki_nazro_ne_samjha.htm"><img src="/images/105x63/aap_ki_nazro_ne_samjha.jpg" width="105" height="63" alt="screen shot of song - Aap Ki Nazro Ne Samjha, Pyar Ke Kabil Mujhe"></a></td>
		   <td rowspan="2">
		         <a href="/song/aap_ki_nazro_ne_samjha.htm"  itemprop="url"><span itemprop="name">Aap Ki Nazro Ne Samjha, Pyar Ke Kabil Mujhe</span> </a>
		   </td>
		 </tr>
		</table>
	*/

	rawPage.Find("table[class=\"b1 w760 bgff pad2 allef\"]").Each(func(i int, s *goquery.Selection) {
		sel := s.Find("tr").First().Find("td").Next().First()
		anchor := sel.Find("a")
		track := strings.TrimSpace(anchor.Text())
		lyricsURL, _ := anchor.Attr("href")
		lyricsURL = strings.TrimSpace(lyricsURL)

		if len(track) == 0 || len(lyricsURL) == 0 {
			log.Printf("track %s or lyricsURL %s are empty\n", track, lyricsURL)
			return
		}
		if lyricsFileMap[track] == nil {
			lyricsFileMap[track] = make(map[string]bool)
		}
		lyricsFileMap[track][lyricsURL] = true
	})
	return nil
}
