import { Singer } from './singer';
import { Composer } from './composer';
import { Writer } from './writer';

export interface TrackItem {
    id: number;
    title_en: string;
    composers: string;
    singers: string;
    writers: string;
    releaseYear: number;
    lyrics: string;
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
