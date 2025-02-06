import { Injectable } from '@angular/core';
import { TrackItem } from '../models/track';
import { Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class TrackService {

  // constructor(private httpClient: HttpClient) { }

  getElements(searchText: string | undefined) {
    console.log('searchText kk: ', searchText);
    if (searchText == "1") {
      return ELEMENT_DATA.slice(0,1);
    } else if (searchText == "2") {
      return ELEMENT_DATA.slice(1,2);
    } else if (searchText == "3") {
      return ELEMENT_DATA.slice(0,2);
    } else {
      return ELEMENT_DATA;
    }
  }


}

const ELEMENT_DATA: TrackItem[] = [
  {
    id: 1,
    title: 'Title 1',
    composers: 'c1',
    singers: 'H1',
    writers: 'w1',
    releaseYear: 1,
    lyrics: `Hydrogen is a chemical element with symbol H and atomic number 1. With a standard
        atomic weight of 1.008, hydrogen is the lightest element on the periodic table.`
  }, {
    id: 2,
    title: 'Title 2',
    composers: 'c2',
    singers: 'H2',
    writers: 'w2',
    releaseYear: 2,
    lyrics: `Helium is a chemical element with symbol He and atomic number 2. It is a
        colorless, odorless, tasteless, non-toxic, inert, monatomic gas, the first in the noble gas
        group in the periodic table. Its boiling point is the lowest among all the elements.`
  }, {
    id: 3,
    title: 'Title 3',
    composers: 'c3',
    singers: 'H3',
    writers: 'w3',
    releaseYear: 1,
    lyrics: `Lithium is a chemical element with symbol Li and atomic number 3. It is a soft,
        silvery-white alkali metal. Under standard conditions, it is the lightest metal and the
        lightest solid element.`
  }, {
    id: 4,
    title: 'Title 4',
    composers: 'c4',
    singers: 'H4',
    writers: 'w4',
    releaseYear: 4,
    lyrics: `Beryllium is a chemical element with symbol Be and atomic number 4. It is a
        relatively rare element in the universe, usually occurring as a product of the spallation of
        larger atomic nuclei that have collided with cosmic rays.`
  }, {
    id: 5,
    title: 'Title 5',
    composers: 'c5',
    singers: 'H5',
    writers: 'w5',
    releaseYear: 5,
    lyrics: `Boron is a chemical element with symbol B and atomic number 5. Produced entirely
        by cosmic ray spallation and supernovae and not by stellar nucleosynthesis, it is a
        low-abundance element in the Solar system and in the Earth's crust.`,
  }]