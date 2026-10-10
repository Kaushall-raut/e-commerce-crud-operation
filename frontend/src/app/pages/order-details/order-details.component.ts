import { CommonModule, CurrencyPipe } from "@angular/common";
import { Component, OnInit, inject } from "@angular/core";
import { FormBuilder, ReactiveFormsModule, Validators } from "@angular/forms";
import {
  Order,
  OrderDetail,
  OrderDetailPayload,
  Product,
} from "../../core/models/api.models";
import { OrderDetailService } from "../../core/services/order-detail.service";
import { OrderService } from "../../core/services/order.service";
import { ProductService } from "../../core/services/product.service";
import { apiErrorMessage } from "../../core/services/api-error";

@Component({
  selector: "app-order-details",
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, CurrencyPipe],
  templateUrl: "./order-details.component.html",
})
export class OrderDetailsComponent implements OnInit {
  private readonly service = inject(OrderDetailService);
  private readonly orderService = inject(OrderService);
  private readonly productService = inject(ProductService);
  private readonly fb = inject(FormBuilder);
  readonly pageSize = 10;
  details: OrderDetail[] = [];
  orders: Order[] = [];
  products: Product[] = [];
  total = 0;
  page = 1;
  loading = false;
  saving = false;
  error = "";
  success = "";
  orderFilter = "";
  editingId: number | null = null;
  form = this.fb.nonNullable.group({
    order_id: [0, [Validators.required, Validators.min(1)]],
    product_id: [0, [Validators.required, Validators.min(1)]],
    quantity: [1, [Validators.required, Validators.min(1)]],
  });

  ngOnInit(): void {
    this.load();
    this.orderService
      .list(1, 100)
      .subscribe({
        next: (data) => (this.orders = data.items),
        error: (err) => (this.error = apiErrorMessage(err)),
      });
    this.productService
      .list(1, 100)
      .subscribe({
        next: (data) => (this.products = data.items),
        error: (err) => (this.error = apiErrorMessage(err)),
      });
  }
  load(): void {
    this.loading = true;
    this.service
      .list(
        this.page,
        this.pageSize,
        this.orderFilter ? Number(this.orderFilter) : undefined,
      )
      .subscribe({
        next: (data) => {
          this.details = data.items;
          this.total = data.total;
          this.loading = false;
        },
        error: (err) => {
          this.error = apiErrorMessage(err);
          this.loading = false;
        },
      });
  }
  applyFilter(): void {
    this.page = 1;
    this.load();
  }
  setOrderFilter(orderId: number): void {
    this.orderFilter = String(orderId);
    this.applyFilter();
  }
  changePage(next: number): void {
    this.page = next;
    this.load();
  }
  currentProduct(): Product | undefined {
    return this.products.find(
      (item) => item.product_id === Number(this.form.controls.product_id.value),
    );
  }
  newDetail(): void {
    this.editingId = null;
    this.form.reset({
      order_id: this.orderFilter ? Number(this.orderFilter) : 0,
      product_id: 0,
      quantity: 1,
    });
    this.error = "";
  }
  edit(item: OrderDetail): void {
    this.editingId = item.order_detail_id;
    this.form.reset({
      order_id: item.order_id,
      product_id: item.product_id,
      quantity: item.quantity,
    });
    this.error = "";
    this.success = "";
  }
  save(): void {
    this.form.markAllAsTouched();
    if (this.form.invalid || this.saving) return;
    const raw = this.form.getRawValue();
    const payload: OrderDetailPayload = {
      order_id: Number(raw.order_id),
      product_id: Number(raw.product_id),
      quantity: Number(raw.quantity),
    };
    const wasEditing = this.editingId !== null;
    this.saving = true;
    this.error = "";
    this.success = "";
    const request = wasEditing
      ? this.service.update(this.editingId!, payload)
      : this.service.create(payload);
    request.subscribe({
      next: (saved) => {
        this.saving = false;
        this.success = wasEditing
          ? "Line item updated. Stock and order subtotal were recalculated."
          : `Added ${saved.product_name || "product"} to order #${saved.order_id}. Stock and subtotal updated.`;
        this.editingId = null;
        this.form.reset({
          order_id: this.orderFilter ? Number(this.orderFilter) : 0,
          product_id: 0,
          quantity: 1,
        });
        this.load();
        this.productService
          .list(1, 100)
          .subscribe({ next: (data) => (this.products = data.items) });
        this.orderService
          .list(1, 100)
          .subscribe({ next: (data) => (this.orders = data.items) });
      },
      error: (err) => {
        this.saving = false;
        this.error = apiErrorMessage(err);
      },
    });
  }
  remove(item: OrderDetail): void {
    if (
      !confirm(
        `Remove "${item.product_name || "this product"}" from order #${item.order_id}? ${item.quantity} unit(s) will be restored to stock.`,
      )
    )
      return;
    this.service.delete(item.order_detail_id).subscribe({
      next: () => {
        this.success =
          "Line item removed. Stock and order subtotal were recalculated.";
        if (this.details.length === 1 && this.page > 1) this.page--;
        this.load();
        this.productService
          .list(1, 100)
          .subscribe({ next: (data) => (this.products = data.items) });
        this.orderService
          .list(1, 100)
          .subscribe({ next: (data) => (this.orders = data.items) });
      },
      error: (err) => (this.error = apiErrorMessage(err)),
    });
  }
}
