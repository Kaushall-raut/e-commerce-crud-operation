import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { OrderDetail, OrderDetailPayload, Page } from '../models/api.models';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class OrderDetailService {
  private readonly http = inject(HttpClient);
  private readonly url = `${environment.apiBaseUrl}/order-details`;

  list(page = 1, pageSize = 100, orderId?: number): Observable<Page<OrderDetail>> {
    let params = new HttpParams().set('page', page).set('page_size', pageSize);
    if (orderId) params = params.set('order_id', orderId);
    return this.http.get<Page<OrderDetail>>(this.url, { params });
  }
  get(id: number): Observable<OrderDetail> { return this.http.get<OrderDetail>(`${this.url}/${id}`); }
  create(payload: OrderDetailPayload): Observable<OrderDetail> { return this.http.post<OrderDetail>(this.url, payload); }
  update(id: number, payload: OrderDetailPayload): Observable<OrderDetail> { return this.http.put<OrderDetail>(`${this.url}/${id}`, payload); }
  delete(id: number): Observable<void> { return this.http.delete<void>(`${this.url}/${id}`); }
}
