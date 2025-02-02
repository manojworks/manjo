import { Component , Output, EventEmitter} from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-search',
  standalone: true,
  imports: [FormsModule],
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
