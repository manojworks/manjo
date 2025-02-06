import { Component , OnInit, Output, EventEmitter} from '@angular/core';
import { FormsModule } from '@angular/forms';
import {RouterModule } from '@angular/router';
import {animate, state, style, transition, trigger} from '@angular/animations';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { ActivatedRoute } from '@angular/router';
import { TrackService } from '../../services/track.service';
import { CommonModule } from '@angular/common'
import { TrackItem } from '../../models/track';

@Component({
  selector: 'app-search',
  standalone: true,
  imports: [FormsModule, RouterModule, MatTableModule, CommonModule],
  templateUrl: './search.component.html',
  styleUrl: './search.component.css',
  animations: [
      trigger('detailExpand', [
        state('collapsed', style({height: '0px', minHeight: '0'})),
        state('expanded', style({height: '*'})),
        transition('expanded <=> collapsed', animate('225ms ease(0.4, 0.0, 0.2, 1)')),
      ]),
    ],
})
export class SearchComponent implements OnInit {

  searchText = '';
  dataSource = new MatTableDataSource<TrackItem>();

  @Output() searchFilterTextEvent = new EventEmitter<string>();

  constructor(
    private activatedRoute: ActivatedRoute,
    private trackService: TrackService,
  ) {}

  ngOnInit(): void {

    this.dataSource = new MatTableDataSource(this.trackService.getElements("1"));

    this.activatedRoute.queryParams.subscribe((params) => {
      this.searchText = params['searchText'];
      if (!this.searchText) {
        this.searchText = '';
      } else {
        this.getTracks(this.searchText);
      }
    });
  }

  sendSearchFilterText() {
    this.searchFilterTextEvent.emit(this.searchText);
    
    if (this.searchText) {
      this.getTracks(this.searchText);
    }
  }

  getTracks(searchText: string) {
    
    console.log('searchText: ', searchText);
    this.dataSource = new MatTableDataSource(this.trackService.getElements(searchText));
  }

  columnsToDisplay = ['title', 'singers', 'composers',  'writers'];
    expandedTrack: TrackItem | null = null;
    expandedTracks: TrackItem[] = [];
  
    public isExpanded(element: { title: string; }) {
      return this.expandedTracks.find(c => c.title === element.title) ? true : false;
    }
  
    public hideExpandedElement(element: { title: string; }): void {
      const index = this.expandedTracks.findIndex(c => c.title === element.title);
      if (index > -1) {
        this.expandedTracks.splice(index, 1);
      }
    }
  
    public showExpandedElement(element: TrackItem): void {
      this.expandedTracks.push(element);
    }
}
