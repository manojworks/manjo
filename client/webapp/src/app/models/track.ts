import { Singer } from './singer';
import { Composer } from './composer';
import { Writer } from './writer';

export interface TrackItem {
    id: number;
    title: string;
    composers: string;
    singers: string;
    writers: string;
    releaseYear: number;
    description: string;
}

export interface Track {
    id: number;
    title: string;
    composers: Composer[];
    singers: Singer[];
    writers: Writer[];
    releaseYear: number;
    description: number;
}
