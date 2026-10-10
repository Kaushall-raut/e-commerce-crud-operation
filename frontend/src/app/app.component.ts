import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  template: `
    <div class="min-h-screen bg-[#f7f8fc] text-slate-800">
      <aside class="fixed inset-y-0 left-0 z-40 flex w-[248px] flex-col border-r border-slate-200 bg-white transition-transform lg:translate-x-0"
             [class.-translate-x-full]="!mobileMenuOpen" [class.translate-x-0]="mobileMenuOpen">
        <div class="flex h-[82px] items-center gap-3 border-b border-slate-100 px-6">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-md shadow-indigo-200">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="h-6 w-6"><path d="M3 8h18l-1.5 12h-15L3 8Z"/><path d="M8 9V6a4 4 0 0 1 8 0v3"/><path d="M8 13h.01M16 13h.01" stroke-linecap="round"/></svg>
          </div>
          <div><div class="text-[17px] font-extrabold tracking-tight text-slate-900">E-Commerce</div><div class="mt-0.5 text-[10px] font-bold uppercase tracking-[.15em] text-slate-400">Store management</div></div>
          <button class="ml-auto rounded-lg p-1 text-slate-400 lg:hidden" aria-label="Close navigation" (click)="mobileMenuOpen = false">✕</button>
        </div>
        <div class="px-4 pt-7">
          <div class="mb-3 px-3 text-[10px] font-extrabold uppercase tracking-[.14em] text-slate-400">Workspace</div>
          <nav class="space-y-1">
            <a routerLink="/dashboard" routerLinkActive="bg-indigo-50 text-indigo-700" [routerLinkActiveOptions]="{ exact: true }" (click)="mobileMenuOpen = false" class="nav-item"><span class="nav-icon">▦</span>Overview</a>
            <a routerLink="/customers" routerLinkActive="bg-indigo-50 text-indigo-700" (click)="mobileMenuOpen = false" class="nav-item"><span class="nav-icon">♙</span>Customers</a>
            <a routerLink="/products" routerLinkActive="bg-indigo-50 text-indigo-700" (click)="mobileMenuOpen = false" class="nav-item"><span class="nav-icon">▤</span>Products <span class="nav-dot"></span></a>
            <a routerLink="/orders" routerLinkActive="bg-indigo-50 text-indigo-700" (click)="mobileMenuOpen = false" class="nav-item"><span class="nav-icon">▣</span>Orders</a>
            <a routerLink="/order-details" routerLinkActive="bg-indigo-50 text-indigo-700" (click)="mobileMenuOpen = false" class="nav-item"><span class="nav-icon">☷</span>Order details</a>
          </nav>
        </div>
        
      </aside>
      @if (mobileMenuOpen) {
        <button class="fixed inset-0 z-30 bg-slate-950/30 lg:hidden" aria-label="Close navigation overlay" (click)="mobileMenuOpen = false"></button>
      }
      <div class="min-h-screen lg:pl-[248px]">
        <header class="sticky top-0 z-20 flex h-[74px] items-center justify-between border-b border-slate-200/80 bg-white/90 px-4 backdrop-blur sm:px-7 lg:px-9">
          <div class="flex items-center gap-3">
            <button class="rounded-xl border border-slate-200 p-2 text-slate-600 lg:hidden" aria-label="Open navigation" (click)="mobileMenuOpen = true">☰</button>
            <div><div class="text-[11px] font-semibold text-slate-400">Workspace / <span class="text-indigo-600">Management</span></div><div class="mt-1 text-sm font-extrabold text-slate-800">E-commerce operations</div></div>
          </div>
          <div class="flex items-center gap-3">
            <div class="hidden rounded-full border border-slate-200 bg-slate-50 px-3 py-2 text-[11px] font-semibold text-slate-500 sm:block">● <span class="ml-1">Admin workspace</span></div>
            <div class="flex h-9 w-9 items-center justify-center rounded-full bg-indigo-100 text-xs font-extrabold text-indigo-700">CA</div>
          </div>
        </header>
        <main class="mx-auto max-w-[1500px] p-4 sm:p-7 lg:p-9"><router-outlet /></main>
        <footer class="px-6 pb-7 text-center text-[11px] text-slate-400">CommerceDesk · E-commerce management · Built for your store operations</footer>
      </div>
    </div>
  `,
  styles: [`
    .nav-item { display:flex; align-items:center; gap:12px; border-radius:11px; padding:11px 13px; color:#687386; font-size:13px; font-weight:650; transition:all .15s; }
    .nav-item:hover { background:#f8fafc; color:#394150; }
    .nav-item.bg-indigo-50 { color:#4338ca; }
    .nav-icon { width:18px; text-align:center; font-size:18px; line-height:1; }
    .nav-dot { margin-left:auto; width:6px; height:6px; border-radius:999px; background:#f59e0b; }
  `]
})
export class AppComponent {
  mobileMenuOpen = false;
}
