import { Component , Output, EventEmitter} from '@angular/core';
import { FormsModule } from '@angular/forms';
import {RouterModule } from '@angular/router';
import { TrackListComponent } from "../track-list/track-list.component";

@Component({
  selector: 'app-search',
  standalone: true,
  imports: [FormsModule, RouterModule, TrackListComponent],
  templateUrl: './search.component.html',
  styleUrl: './search.component.css'
})
export class SearchComponent {

  searchText = '';

  @Output() searchFilterTextEvent = new EventEmitter<string>();

  sendSearchFilterText() {
    this.searchFilterTextEvent.emit(this.searchText);
    console.log('searchText: ', this.searchText);
  }
}
