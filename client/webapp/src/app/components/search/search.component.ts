import { Component , OnInit, Output, EventEmitter, ElementRef, HostListener, ViewChild, output} from '@angular/core';
import { FormsModule } from '@angular/forms';
import {RouterModule } from '@angular/router';
import {animate, state, style, transition, trigger} from '@angular/animations';
import { MatTableDataSource, MatTableModule, MatTable} from '@angular/material/table';
import { SongDropDownAttributes } from '../../models/songdropdownattributes';
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

  // @Output() searchFilterTextEvent = new EventEmitter<string>();
  searchFilterTextEvent = output<string>();

  constructor(
    private activatedRoute: ActivatedRoute,
    private trackService: TrackService,
  ) {}

  ngOnInit(): void {

    //TODO: change to 10 user configured value
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

    columnsToDisplay = ['title_en', 'album', 'singers', 'composers',  'writers'];
    expandedTrack: TrackItem | null = null;
    expandedTracks: TrackItem[] = [];
  
    //TODO: comparison with title to expand/collapse is a problem. consider using id
    public isExpanded(element: { title_en: string; }) {
      return this.expandedTracks.find(c => c.title_en === element.title_en) ? true : false;
    }
  
    //TODO: comparison with title to expand/collapse is a problem. consider using id
    public hideExpandedElement(element: { title_en: string; }): void {
      const index = this.expandedTracks.findIndex(c => c.title_en === element.title_en);
      if (index > -1) {
        this.expandedTracks.splice(index, 1);
      }
    }
  
    public showExpandedElement(element: TrackItem): void {
      this.expandedTracks.push(element);
    }

    trackElems: SongDropDownAttributes[] = [ {"id": 'all', display: 'All'}, 
                                                    {"id": 'title_en', display: 'Title'}, 
                                                    {"id": 'album', display: 'Album'}, 
                                                    {"id": 'categories', display: 'Category'}, 
                                                    {"id": 'composers', display: 'Composer'}, 
                                                    {"id": 'singers', display: 'Singer'}, 
                                                    {"id": 'writers', display: 'Writer'}, 
                                                    {"id": 'actors', display: 'Actor'}, 
                                                    {"id": 'lyrics_en', display: 'Lyrics'}, 
                                                    {"id": 'lyrics_hi', display: 'बोल'}];
                                                    
    trackAttributeSelectedValue: {id: string, display: string} = this.trackElems[0];


    clickHandler(item: SongDropDownAttributes) {
      this.trackAttributeSelectedValue = item;
      //this.searchText = this.trackAttributeSelectedValue;
      
    }

    @HostListener('click') hostClick() {
      //this.searchText = this.trackAttributeSelectedValue;
    }

    goSearch() {
      console.log('searchText: ', this.searchText);
      console.log('trackAttributeSelectedValue: ', this.trackAttributeSelectedValue);
      this.trackService.searchTracks(this.searchText, this.trackAttributeSelectedValue.id).subscribe((data) => {
        this.dataSource = new MatTableDataSource(data);
      });
    }
}
