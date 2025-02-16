import { Singer } from './singer';
import { Composer } from './composer';
import { Writer } from './writer';

export interface TrackItem {
    id: number;
    title_en: string;
    album: string;
    releaseYear: number;
    duration: number;
    categories: string;
    composers: string;
    singers: string;
    writers: string;
    actors: string;
    lyrics_en: string;
    lyrics_hi: string;
  }
  
  
// export interface Track {
//     id: number;
//     title_en: string;
//     composers: Composer[];
//     singers: Singer[];
//     writers: Writer[];
//     releaseYear: number;
//     lyrics: string;
// }
