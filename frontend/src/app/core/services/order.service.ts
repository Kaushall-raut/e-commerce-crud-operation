import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Order, OrderPayload, OrderWithDetails, Page } from '../models/api.models';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class OrderService {
  private readonly http = inject(HttpClient);
  private readonly url = `${environment.apiBaseUrl}/orders`;

  list(page = 1, pageSize = 100): Observable<Page<Order>> {
    const params = new HttpParams().set('page', page).set('page_size', pageSize);
    return this.http.get<Page<Order>>(this.url, { params });
  }
  get(id: number): Observable<OrderWithDetails> { return this.http.get<OrderWithDetails>(`${this.url}/${id}`); }
  create(payload: OrderPayload): Observable<Order> { return this.http.post<Order>(this.url, payload); }
  update(id: number, payload: OrderPayload): Observable<Order> { return this.http.put<Order>(`${this.url}/${id}`, payload); }
  delete(id: number): Observable<void> { return this.http.delete<void>(`${this.url}/${id}`); }
}
