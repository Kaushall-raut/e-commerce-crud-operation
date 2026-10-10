export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface Customer {
  customer_id: number;
  customer_name: string;
  customer_contact: string;
  customer_gender: string | null;
}

export type CustomerPayload = Omit<Customer, 'customer_id'>;

export interface Product {
  product_id: number;
  product_image: string | null;
  product_name: string;
  product_stock: number;
  product_price: string | number;
}

export type ProductPayload = Omit<Product, 'product_id'>;

export interface Order {
  order_id: number;
  order_datetime: string;
  total_price: string | number;
  discount: string | number;
  customer_id: number;
  customer_name: string | null;
  final_payable: string | number;
}

export interface OrderPayload {
  order_datetime?: string | null;
  discount: string | number;
  customer_id: number;
}

export interface OrderDetail {
  order_detail_id: number;
  order_id: number;
  product_id: number;
  product_name: string | null;
  quantity: number;
  unit_price: string | number;
  total_price: string | number;
}

export interface OrderDetailPayload {
  order_id: number;
  product_id: number;
  quantity: number;
}

export interface TopProduct {
  product_id: number;
  product_name: string;
  units_sold: number;
  revenue: string | number;
}

export interface DashboardSummary {
  total_customers: number;
  total_products: number;
  total_orders: number;
  total_sales: string | number;
  total_discounts: string | number;
  low_stock_products: Product[];
  recent_orders: Order[];
  best_selling_products: TopProduct[];
}

export interface OrderWithDetails extends Order {
  details: OrderDetail[];
}
