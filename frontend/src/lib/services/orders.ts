/**
 * Orders and Cart API Services
 */

import { api } from '../api';
import {
  Cart,
  CartItem,
  AddToCartRequest,
  Order,
  CreateOrderRequest,
  ShippingMethod,
  Discount,
  ApplyDiscountRequest,
  DiscountResponse,
  CheckoutCalculation,
} from '../../types/api';

export const orderService = {
  // Cart management
  getCart: async (): Promise<Cart> => {
    return api.get('/orders/cart/');
  },

  addToCart: async (data: AddToCartRequest): Promise<CartItem> => {
    return api.post('/orders/cart/add/', data);
  },

  updateCartItem: async (itemId: number, quantity: number): Promise<CartItem> => {
    return api.patch(`/orders/cart/items/${itemId}/`, { quantity });
  },

  removeFromCart: async (itemId: number): Promise<void> => {
    return api.delete(`/orders/cart/items/${itemId}/remove/`);
  },

  clearCart: async (): Promise<{ message: string }> => {
    return api.post('/orders/cart/clear/');
  },

  // Orders
  getOrders: async (): Promise<Order[]> => {
    return api.get('/orders/');
  },

  createOrder: async (orderData: CreateOrderRequest): Promise<Order> => {
    return api.post('/orders/', orderData);
  },

  getOrder: async (orderNumber: string): Promise<Order> => {
    return api.get(`/orders/${orderNumber}/`);
  },

  cancelOrder: async (orderNumber: string): Promise<{ message: string }> => {
    return api.post(`/orders/${orderNumber}/cancel/`);
  },

  // Shipping methods
  getShippingMethods: async (): Promise<ShippingMethod[]> => {
    return api.get('/orders/shipping-methods/');
  },

  // Discounts
  applyDiscount: async (data: ApplyDiscountRequest): Promise<DiscountResponse> => {
    return api.post('/orders/discounts/apply/', data);
  },

  // Checkout calculations
  getCheckoutCalculation: async (discountCode?: string, shippingCost?: number): Promise<CheckoutCalculation> => {
    const params: any = {};
    if (discountCode) params.discount_code = discountCode;
    if (shippingCost) params.shipping_cost = shippingCost;
    
    return api.get('/orders/checkout/calculate/', params);
  },
};
