/**
 * Shopping and Cart React Query Hooks
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { orderService } from '../lib/services/orders';
import { authUtils } from '../lib/api';
import {
  Cart,
  CartItem,
  AddToCartRequest,
  Order,
  CreateOrderRequest,
  ShippingMethod,
  ApplyDiscountRequest,
} from '../types/api';

// Query Keys
export const SHOPPING_KEYS = {
  cart: ['shopping', 'cart'] as const,
  orders: ['shopping', 'orders'] as const,
  order: (orderNumber: string) => ['shopping', 'order', orderNumber] as const,
  shippingMethods: ['shopping', 'shippingMethods'] as const,
  checkoutCalculation: (params?: any) => ['shopping', 'checkout', params] as const,
};

// Cart Hooks
export const useCart = () => {
  return useQuery({
    queryKey: SHOPPING_KEYS.cart,
    queryFn: orderService.getCart,
    enabled: authUtils.isAuthenticated(),
    staleTime: 1 * 60 * 1000, // 1 minute
  });
};

export const useAddToCart = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: AddToCartRequest) => orderService.addToCart(data),
    onSuccess: () => {
      // Invalidate cart to refresh data
      queryClient.invalidateQueries({ queryKey: SHOPPING_KEYS.cart });
    },
  });
};

export const useUpdateCartItem = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ itemId, quantity }: { itemId: number; quantity: number }) => 
      orderService.updateCartItem(itemId, quantity),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: SHOPPING_KEYS.cart });
    },
  });
};

export const useRemoveFromCart = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (itemId: number) => orderService.removeFromCart(itemId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: SHOPPING_KEYS.cart });
    },
  });
};

export const useClearCart = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: orderService.clearCart,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: SHOPPING_KEYS.cart });
    },
  });
};

// Order Hooks
export const useOrders = () => {
  return useQuery({
    queryKey: SHOPPING_KEYS.orders,
    queryFn: orderService.getOrders,
    enabled: authUtils.isAuthenticated(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useOrder = (orderNumber: string) => {
  return useQuery({
    queryKey: SHOPPING_KEYS.order(orderNumber),
    queryFn: () => orderService.getOrder(orderNumber),
    enabled: authUtils.isAuthenticated() && !!orderNumber,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useCreateOrder = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (orderData: CreateOrderRequest) => orderService.createOrder(orderData),
    onSuccess: () => {
      // Invalidate cart and orders
      queryClient.invalidateQueries({ queryKey: SHOPPING_KEYS.cart });
      queryClient.invalidateQueries({ queryKey: SHOPPING_KEYS.orders });
    },
  });
};

export const useCancelOrder = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (orderNumber: string) => orderService.cancelOrder(orderNumber),
    onSuccess: (_, orderNumber) => {
      // Invalidate orders and specific order
      queryClient.invalidateQueries({ queryKey: SHOPPING_KEYS.orders });
      queryClient.invalidateQueries({ queryKey: SHOPPING_KEYS.order(orderNumber) });
    },
  });
};

// Shipping and Checkout Hooks
export const useShippingMethods = () => {
  return useQuery({
    queryKey: SHOPPING_KEYS.shippingMethods,
    queryFn: orderService.getShippingMethods,
    staleTime: 30 * 60 * 1000, // 30 minutes
  });
};

export const useApplyDiscount = () => {
  return useMutation({
    mutationFn: (data: ApplyDiscountRequest) => orderService.applyDiscount(data),
  });
};

export const useCheckoutCalculation = (discountCode?: string, shippingCost?: number) => {
  return useQuery({
    queryKey: SHOPPING_KEYS.checkoutCalculation({ discountCode, shippingCost }),
    queryFn: () => orderService.getCheckoutCalculation(discountCode, shippingCost),
    enabled: authUtils.isAuthenticated(),
    staleTime: 30 * 1000, // 30 seconds
  });
};

// Utility Hook for Cart Count
export const useCartCount = () => {
  const { data: cart } = useCart();
  return cart?.total_items ?? 0;
};
