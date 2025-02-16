import { Component , OnInit, Output, EventEmitter, ElementRef, HostListener, ViewChild} from '@angular/core';
import { FormsModule } from '@angular/forms';
import {RouterModule } from '@angular/router';
import {animate, state, style, transition, trigger} from '@angular/animations';
import { MatTableDataSource, MatTableModule, MatTable} from '@angular/material/table';
import { MatFormField } from '@angular/material/form-field';
import {MatSelectModule} from '@angular/material/select';
import {MatOptionModule} from '@angular/material/core';
import { ActivatedRoute } from '@angular/router';
import { TrackService } from '../../services/track.service';
import { CommonModule } from '@angular/common'
import { TrackItem } from '../../models/track';

@Component({
  selector: 'app-search',
  standalone: true,
  imports: [FormsModule, RouterModule, MatTableModule, CommonModule, MatSelectModule, MatOptionModule, ],
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

    // this.dataSource = new MatTableDataSource(this.trackService.popularTracks(10));
    this.trackService.popularTracks(10).subscribe((data) => {
      this.dataSource = new MatTableDataSource(data);
    });

  }

  //TODO: Do I need this?
  sendSearchFilterText() {
    // this.searchFilterTextEvent.emit(this.searchText);
    
    // if (this.searchText) {
    //   this.getTracks(this.searchText);
    // }
  }

  getTracks(searchText: string) {
    
    console.log('seadrrrchText: ', searchText);
    // this.dataSource = new MatTableDataSource(this.trackService.getElements(searchText));
  }

    columnsToDisplay = ['title_en', 'singers', 'composers',  'writers'];
    expandedTrack: TrackItem | null = null;
    expandedTracks: TrackItem[] = [];
  
    public isExpanded(element: { title_en: string; }) {
      return this.expandedTracks.find(c => c.title_en === element.title_en) ? true : false;
    }
  
    public hideExpandedElement(element: { title_en: string; }): void {
      const index = this.expandedTracks.findIndex(c => c.title_en === element.title_en);
      if (index > -1) {
        this.expandedTracks.splice(index, 1);
      }
    }
  
    public showExpandedElement(element: TrackItem): void {
      this.expandedTracks.push(element);
    }

    trackElems: string[] = ['all', 'title', 'singer', 'composer',  'writer', 'lyrics', 'actor'];
    trackAttributeSelectedValue: string = this.trackElems[0];


    clickHandler(item: string) {
      this.trackAttributeSelectedValue = item;
      //this.searchText = this.trackAttributeSelectedValue;
      
    }

    @HostListener('click') hostClick() {
      //this.searchText = this.trackAttributeSelectedValue;
    }

    goSearch() {
      console.log('searchText: ', this.searchText);
      console.log('trackAttributeSelectedValue: ', this.trackAttributeSelectedValue);
    }
}
