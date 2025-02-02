import { Singer } from './singer';
import { Composer } from './composer';
import { Writer } from './writer';

export interface Track {
    id: number;
    title: string;
    composers: Composer[];
    singers: Singer[];
    writers: Writer[];
    releaseYear: number;
    description: number;
}
