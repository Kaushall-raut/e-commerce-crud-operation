import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Customer, CustomerPayload } from '../../core/models/api.models';
import { CustomerService } from '../../core/services/customer.service';
import { apiErrorMessage } from '../../core/services/api-error';

@Component({
  selector: 'app-customers', standalone: true, imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './customers.Component.html'
})
export class CustomersComponent implements OnInit {
  private readonly service = inject(CustomerService);
  private readonly fb = inject(FormBuilder);
  readonly pageSize = 10;
  customers: Customer[] = [];
  total = 0; page = 1; loading = false; saving = false;
  searchText = ''; appliedSearch = '';
  error = ''; success = '';
  editingId: number | null = null;
  selected: Customer | null = null;
  form = this.fb.nonNullable.group({
    customer_name: ['', [Validators.required, Validators.maxLength(100)]],
    customer_contact: ['', [Validators.required, Validators.minLength(7), Validators.maxLength(15), Validators.pattern(/^[0-9+() -]+$/)]],
    customer_gender: ['']
  });

  ngOnInit(): void { this.load(); }
  load(): void {
    this.loading = true; this.error = '';
    this.service.list(this.page, this.pageSize, this.appliedSearch).subscribe({
      next: (data) => { this.customers = data.items; this.total = data.total; this.loading = false; },
      error: (err) => { this.error = apiErrorMessage(err); this.loading = false; }
    });
  }
  applySearch(): void { this.page = 1; this.appliedSearch = this.searchText.trim(); this.load(); }
  changePage(nextPage: number): void { this.page = nextPage; this.load(); }
  initials(name: string): string { return name.trim().split(/\s+/).slice(0, 2).map((part) => part[0]?.toUpperCase() ?? '').join(''); }
  view(customer: Customer): void { this.selected = customer; this.editingId = null; }
  newCustomer(): void { this.editingId = null; this.form.reset({ customer_name: '', customer_contact: '', customer_gender: '' }); this.error = ''; this.success = ''; }
  edit(customer: Customer): void {
    this.selected = customer; this.editingId = customer.customer_id;
    this.form.reset({ customer_name: customer.customer_name, customer_contact: customer.customer_contact, customer_gender: customer.customer_gender ?? '' });
    this.error = ''; this.success = '';
  }
  save(): void {
    this.form.markAllAsTouched(); if (this.form.invalid || this.saving) return;
    const raw = this.form.getRawValue();
    const payload: CustomerPayload = { customer_name: raw.customer_name.trim(), customer_contact: raw.customer_contact.trim(), customer_gender: raw.customer_gender.trim() || null };
    this.saving = true; this.error = ''; this.success = '';
    const wasEditing = this.editingId !== null;
    const request = wasEditing ? this.service.update(this.editingId!, payload) : this.service.create(payload);
    request.subscribe({
      next: (saved) => { this.saving = false; this.success = wasEditing ? 'Customer updated successfully.' : 'Customer created successfully.'; this.selected = saved; this.editingId = null; this.form.reset({ customer_name: '', customer_contact: '', customer_gender: '' }); this.load(); },
      error: (err) => { this.saving = false; this.error = apiErrorMessage(err); }
    });
  }
  remove(customer: Customer): void {
    if (!confirm(`Delete customer "${customer.customer_name}"? Customers with existing orders cannot be deleted.`)) return;
    this.service.delete(customer.customer_id).subscribe({
      next: () => { this.success = 'Customer deleted successfully.'; if (this.selected?.customer_id === customer.customer_id) this.selected = null; if (this.customers.length === 1 && this.page > 1) this.page--; this.load(); },
      error: (err) => { this.error = apiErrorMessage(err); }
    });
  }
}
