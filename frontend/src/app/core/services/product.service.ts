import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Page, Product, ProductPayload } from '../models/api.models';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ProductService {
  private readonly http = inject(HttpClient);
  private readonly url = `${environment.apiBaseUrl}/products`;

  list(page = 1, pageSize = 100, q = '', stock = 'all'): Observable<Page<Product>> {
    let params = new HttpParams().set('page', page).set('page_size', pageSize).set('stock', stock);
    if (q.trim()) params = params.set('q', q.trim());
    return this.http.get<Page<Product>>(this.url, { params });
  }
  get(id: number): Observable<Product> { return this.http.get<Product>(`${this.url}/${id}`); }
  create(payload: ProductPayload): Observable<Product> { return this.http.post<Product>(this.url, payload); }
  update(id: number, payload: ProductPayload): Observable<Product> { return this.http.put<Product>(`${this.url}/${id}`, payload); }
  delete(id: number): Observable<void> { return this.http.delete<void>(`${this.url}/${id}`); }
}
