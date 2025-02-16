import { Injectable } from '@angular/core';
import { TrackItem } from '../models/track';
import { Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';


@Injectable({
  providedIn: 'root'
})

export class TrackService {

  apiControllerUrl = `${environment.apiUrl}/songs`;

  constructor(private httpClient: HttpClient) { }

  popularTracks(topK: number): Observable<TrackItem[]> {
    return this.httpClient.get<TrackItem[]>(
      `${this.apiControllerUrl}/popular/${topK}`
  );
  }
}