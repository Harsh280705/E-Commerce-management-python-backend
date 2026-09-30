import { createRouter, createWebHistory } from 'vue-router'

import Home from '../views/Home.vue'
import ProductDetail from '../views/ProductDetail.vue'
import Cart from '../views/Cart.vue'
import Checkout from '../views/Checkout.vue'
import OrderConfirmation from '../views/OrderConfirmation.vue'
import OrderHistory from '../views/OrderHistory.vue'
import OrderDetail from '../views/OrderDetail.vue'
import Admin from '../views/Admin.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import AdminProducts from '../views/AdminProducts.vue'
import AdminOrders from '../views/AdminOrders.vue'
import AdminOrderDetail from '../views/AdminOrderDetail.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Home },
    { path: '/products/:id', component: ProductDetail },
    { path: '/cart', component: Cart },
    { path: '/checkout', component: Checkout },
    { path: '/confirmation/:id', component: OrderConfirmation },
    { path: '/orders', component: OrderHistory },
    { path: '/orders/:id', component: OrderDetail },
    {
      path: '/admin',
      component: Admin,
      children: [
        { path: '', component: AdminDashboard },
        { path: 'products', component: AdminProducts },
        { path: 'orders', component: AdminOrders },
        { path: 'orders/:id', component: AdminOrderDetail }
      ]
    }
  ]
})
