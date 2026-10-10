import { CommonModule, CurrencyPipe, DatePipe } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { Customer, Order, OrderPayload, OrderWithDetails } from '../../core/models/api.models';
import { CustomerService } from '../../core/services/customer.service';
import { OrderService } from '../../core/services/order.service';
import { apiErrorMessage } from '../../core/services/api-error';

@Component({
  selector: 'app-orders', standalone: true, imports: [CommonModule, ReactiveFormsModule, CurrencyPipe, DatePipe, RouterLink],
  templateUrl:'./orders.component.html'
})
export class OrdersComponent implements OnInit {
  private readonly service = inject(OrderService);
  private readonly customerService = inject(CustomerService);
  private readonly fb = inject(FormBuilder);
  readonly pageSize = 10;
  orders: Order[] = []; customers: Customer[] = [];
  total = 0; page = 1; loading = false; saving = false; error = ''; success = '';
  editingId: number | null = null; selectedOrder: OrderWithDetails | null = null;
  form = this.fb.nonNullable.group({
    customer_id: [0, [Validators.required, Validators.min(1)]],
    order_datetime: [this.localDateTime(), [Validators.maxLength(32)]],
    discount: [0, [Validators.required, Validators.min(0)]]
  });

  ngOnInit(): void {
    this.form.controls.discount.disable();
    this.load();
    this.customerService.list(1, 100).subscribe({ next: (data) => this.customers = data.items, error: (err) => this.error = apiErrorMessage(err) });
  }
  localDateTime(value?: string): string {
    // PostgreSQL TIMESTAMP is timezone-naive, so preserve API wall-clock time when editing.
    if (value) return value.slice(0, 16);
    const date = new Date();
    date.setMinutes(date.getMinutes() - date.getTimezoneOffset());
    return date.toISOString().slice(0, 16);
  }
  load(): void {
    this.loading = true;
    this.service.list(this.page, this.pageSize).subscribe({ next: (data) => { this.orders = data.items; this.total = data.total; this.loading = false; }, error: (err) => { this.error = apiErrorMessage(err); this.loading = false; } });
  }
  changePage(next: number): void { this.page = next; this.load(); }
  newOrder(): void {
    this.editingId = null; this.form.reset({ customer_id: 0, order_datetime: this.localDateTime(), discount: 0 });
    this.form.controls.discount.disable(); this.error = '';
  }
  view(order: Order): void {
    this.service.get(order.order_id).subscribe({ next: (data) => this.selectedOrder = data, error: (err) => this.error = apiErrorMessage(err) });
  }
  edit(order: Order): void {
    this.editingId = order.order_id;
    this.form.reset({ customer_id: order.customer_id, order_datetime: this.localDateTime(order.order_datetime), discount: Number(order.discount) });
    this.form.controls.discount.enable(); this.error = ''; this.success = '';
    this.view(order);
  }
  save(): void {
    this.form.markAllAsTouched(); if (this.form.invalid || this.saving) return;
    const raw = this.form.getRawValue();
    const payload: OrderPayload = { customer_id: Number(raw.customer_id), discount: Number(raw.discount) };
    if (raw.order_datetime) payload.order_datetime = raw.order_datetime;
    else if (this.editingId !== null) payload.order_datetime = null;
    const wasEditing = this.editingId !== null;
    this.saving = true; this.error = ''; this.success = '';
    const request = wasEditing ? this.service.update(this.editingId!, payload) : this.service.create(payload);
    request.subscribe({ next: (saved) => {
      this.saving = false; this.success = wasEditing ? 'Order updated successfully.' : `Order #${saved.order_id} created. Add line items to calculate its subtotal.`;
      this.editingId = null; this.form.reset({ customer_id: 0, order_datetime: this.localDateTime(), discount: 0 }); this.form.controls.discount.disable();
      this.load(); this.view(saved);
    }, error: (err) => { this.saving = false; this.error = apiErrorMessage(err); } });
  }
  remove(order: Order): void {
    if (!confirm(`Delete order #${order.order_id}? Its order details will be removed and item quantities restored to stock.`)) return;
    this.service.delete(order.order_id).subscribe({ next: () => { this.success = `Order #${order.order_id} deleted and stock restored.`; if (this.selectedOrder?.order_id === order.order_id) this.selectedOrder = null; if (this.orders.length === 1 && this.page > 1) this.page--; this.load(); }, error: (err) => this.error = apiErrorMessage(err) });
  }
}
