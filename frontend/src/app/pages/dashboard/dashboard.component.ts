import { CommonModule, CurrencyPipe, DatePipe } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { DashboardSummary } from '../../core/models/api.models';
import { DashboardService } from '../../core/services/dashboard.service';
import { apiErrorMessage } from '../../core/services/api-error';

@Component({
  selector: 'app-dashboard', standalone: true,
  imports: [CommonModule, RouterLink, CurrencyPipe, DatePipe],
  templateUrl:'./dashboard.component.html'
})
export class DashboardComponent implements OnInit {
  private readonly dashboardService = inject(DashboardService);
  loading = true;
  error = '';
  data: DashboardSummary | null = null;

  ngOnInit(): void { this.load(); }
  load(): void {
    this.loading = true; this.error = '';
    this.dashboardService.summary().subscribe({
      next: (value) => { this.data = value; this.loading = false; },
      error: (err) => { this.error = apiErrorMessage(err); this.loading = false; }
    });
  }
  barWidth(sold: number, products: { units_sold: number }[]): number {
    const max = Math.max(1, ...products.map((item) => item.units_sold));
    return Math.max(4, (sold / max) * 100);
  }
  onImageError(event: Event): void { (event.target as HTMLImageElement).style.display = 'none'; }
}
