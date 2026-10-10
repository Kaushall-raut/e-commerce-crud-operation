import { CommonModule, CurrencyPipe } from "@angular/common";
import { Component, OnInit, inject } from "@angular/core";
import { FormBuilder, ReactiveFormsModule, Validators } from "@angular/forms";
import { Product, ProductPayload } from "../../core/models/api.models";
import { ProductService } from "../../core/services/product.service";
import { apiErrorMessage } from "../../core/services/api-error";

@Component({
  selector: "app-products",
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, CurrencyPipe],
  templateUrl: "./products.components.html",
})
export class ProductsComponent implements OnInit {
  private readonly service = inject(ProductService);
  private readonly fb = inject(FormBuilder);
  readonly pageSize = 10;
  products: Product[] = [];
  total = 0;
  page = 1;
  loading = false;
  saving = false;
  error = "";
  success = "";
  searchText = "";
  appliedSearch = "";
  stockFilter = "all";
  editingId: number | null = null;
  selected: Product | null = null;
  form = this.fb.nonNullable.group({
    product_name: ["", [Validators.required, Validators.maxLength(150)]],
    product_image: ["", [Validators.maxLength(500)]],
    product_stock: [0, [Validators.required, Validators.min(0)]],
    product_price: ["0.00", [Validators.required, Validators.min(0)]],
  });

  ngOnInit(): void {
    this.load();
  }
  load(): void {
    this.loading = true;
    this.error = "";
    this.service
      .list(this.page, this.pageSize, this.appliedSearch, this.stockFilter)
      .subscribe({
        next: (data) => {
          this.products = data.items;
          this.total = data.total;
          this.loading = false;
        },
        error: (err) => {
          this.error = apiErrorMessage(err);
          this.loading = false;
        },
      });
  }
  applyFilters(): void {
    this.page = 1;
    this.appliedSearch = this.searchText.trim();
    this.load();
  }
  changePage(next: number): void {
    this.page = next;
    this.load();
  }
  newProduct(): void {
    this.editingId = null;
    this.form.reset({
      product_name: "",
      product_image: "",
      product_stock: 0,
      product_price: "0.00",
    });
    this.error = "";
  }
  view(product: Product): void {
    this.selected = product;
    this.editingId = null;
  }
  edit(product: Product): void {
    this.selected = product;
    this.editingId = product.product_id;
    this.form.reset({
      product_name: product.product_name,
      product_image: product.product_image ?? "",
      product_stock: product.product_stock,
      product_price: String(product.product_price),
    });
    this.error = "";
    this.success = "";
  }
  save(): void {
    this.form.markAllAsTouched();
    if (this.form.invalid || this.saving) return;
    const raw = this.form.getRawValue();
    const payload: ProductPayload = {
      product_name: raw.product_name.trim(),
      product_image: raw.product_image.trim() || null,
      product_stock: Number(raw.product_stock),
      product_price: Number(raw.product_price),
    };
    this.saving = true;
    this.error = "";
    this.success = "";
    const wasEditing = this.editingId !== null;
    const request = wasEditing
      ? this.service.update(this.editingId!, payload)
      : this.service.create(payload);
    request.subscribe({
      next: (saved) => {
        this.saving = false;
        this.success = wasEditing
          ? "Product updated successfully."
          : "Product created successfully.";
        this.selected = saved;
        this.editingId = null;
        this.form.reset({
          product_name: "",
          product_image: "",
          product_stock: 0,
          product_price: "0.00",
        });
        this.load();
      },
      error: (err) => {
        this.saving = false;
        this.error = apiErrorMessage(err);
      },
    });
  }
  remove(product: Product): void {
    if (
      !confirm(
        `Delete product "${product.product_name}"? Products used in order details cannot be deleted.`,
      )
    )
      return;
    this.service.delete(product.product_id).subscribe({
      next: () => {
        this.success = "Product deleted successfully.";
        if (this.selected?.product_id === product.product_id)
          this.selected = null;
        if (this.products.length === 1 && this.page > 1) this.page--;
        this.load();
      },
      error: (err) => {
        this.error = apiErrorMessage(err);
      },
    });
  }
  onImageError(event: Event): void {
    (event.target as HTMLImageElement).style.display = "none";
  }
}
