import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { HomepageComponent } from './components/homepage/homepage.component';
import { SearchComponent } from './components/search/search.component';

export const routes: Routes = [
    { path: '', pathMatch: 'full', component: HomepageComponent },
    { path: 'search', component: SearchComponent },
]

@NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports: [RouterModule],
  })
  export class AppRoutingModule {}
  