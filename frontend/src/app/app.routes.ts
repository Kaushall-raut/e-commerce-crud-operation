import { Routes } from '@angular/router';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { CustomersComponent } from './pages/customers/customers.component';
import { ProductsComponent } from './pages/products/products.component';
import { OrdersComponent } from './pages/orders/orders.component';
import { OrderDetailsComponent } from './pages/order-details/order-details.component';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'dashboard' },
  { path: 'dashboard', component: DashboardComponent, title: 'Dashboard · CommerceDesk' },
  { path: 'customers', component: CustomersComponent, title: 'Customers · CommerceDesk' },
  { path: 'products', component: ProductsComponent, title: 'Products · CommerceDesk' },
  { path: 'orders', component: OrdersComponent, title: 'Orders · CommerceDesk' },
  { path: 'order-details', component: OrderDetailsComponent, title: 'Order details · CommerceDesk' },
  { path: '**', redirectTo: 'dashboard' }
];
