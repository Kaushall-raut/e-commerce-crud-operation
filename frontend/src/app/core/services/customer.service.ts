import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Customer, CustomerPayload, Page } from '../models/api.models';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class CustomerService {
  private readonly http = inject(HttpClient);
  private readonly url = `${environment.apiBaseUrl}/customers`;

  list(page = 1, pageSize = 100, q = ''): Observable<Page<Customer>> {
    let params = new HttpParams().set('page', page).set('page_size', pageSize);
    if (q.trim()) params = params.set('q', q.trim());
    return this.http.get<Page<Customer>>(this.url, { params });
  }
  get(id: number): Observable<Customer> { return this.http.get<Customer>(`${this.url}/${id}`); }
  create(payload: CustomerPayload): Observable<Customer> { return this.http.post<Customer>(this.url, payload); }
  update(id: number, payload: CustomerPayload): Observable<Customer> { return this.http.put<Customer>(`${this.url}/${id}`, payload); }
  delete(id: number): Observable<void> { return this.http.delete<void>(`${this.url}/${id}`); }
}
