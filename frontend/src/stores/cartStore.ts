/**
 * Simple Cart Store for Demo Functionality
 * This provides local cart management until full backend integration
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface CartProduct {
  id: number;
  name: string;
  price: number;
  category_name: string;
  sku: string;
}

interface CartItem {
  id: number;
  product: CartProduct;
  quantity: number;
  unit_price: number;
  total_price: number;
}

interface Cart {
  id: number;
  items: CartItem[];
  total_items: number;
  subtotal: number;
}

interface CartState {
  cart: Cart;
  addToCart: (product: CartProduct, quantity?: number) => void;
  removeFromCart: (itemId: number) => void;
  updateCartItem: (itemId: number, quantity: number) => void;
  clearCart: () => void;
  getCartCount: () => number;
}

const initialCart: Cart = {
  id: 1,
  items: [],
  total_items: 0,
  subtotal: 0,
};

export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      cart: initialCart,
      
      addToCart: (product: CartProduct, quantity = 1) => {
        set((state) => {
          const existingItemIndex = state.cart.items.findIndex(
            item => item.product.id === product.id
          );
          
          let updatedItems: CartItem[];
          
          if (existingItemIndex >= 0) {
            // Update existing item
            updatedItems = state.cart.items.map((item, index) =>
              index === existingItemIndex
                ? {
                    ...item,
                    quantity: item.quantity + quantity,
                    total_price: (item.quantity + quantity) * item.unit_price,
                  }
                : item
            );
          } else {
            // Add new item
            const newItem: CartItem = {
              id: Date.now(), // Simple ID generation
              product,
              quantity,
              unit_price: product.price,
              total_price: product.price * quantity,
            };
            updatedItems = [...state.cart.items, newItem];
          }
          
          const total_items = updatedItems.reduce((sum, item) => sum + item.quantity, 0);
          const subtotal = updatedItems.reduce((sum, item) => sum + item.total_price, 0);
          
          return {
            cart: {
              ...state.cart,
              items: updatedItems,
              total_items,
              subtotal,
            },
          };
        });
      },
      
      removeFromCart: (itemId: number) => {
        set((state) => {
          const updatedItems = state.cart.items.filter(item => item.id !== itemId);
          const total_items = updatedItems.reduce((sum, item) => sum + item.quantity, 0);
          const subtotal = updatedItems.reduce((sum, item) => sum + item.total_price, 0);
          
          return {
            cart: {
              ...state.cart,
              items: updatedItems,
              total_items,
              subtotal,
            },
          };
        });
      },
      
      updateCartItem: (itemId: number, quantity: number) => {
        set((state) => {
          if (quantity <= 0) {
            // Remove item if quantity is 0 or negative
            return get().removeFromCart(itemId);
          }
          
          const updatedItems = state.cart.items.map(item =>
            item.id === itemId
              ? {
                  ...item,
                  quantity,
                  total_price: quantity * item.unit_price,
                }
              : item
          );
          
          const total_items = updatedItems.reduce((sum, item) => sum + item.quantity, 0);
          const subtotal = updatedItems.reduce((sum, item) => sum + item.total_price, 0);
          
          return {
            cart: {
              ...state.cart,
              items: updatedItems,
              total_items,
              subtotal,
            },
          };
        });
      },
      
      clearCart: () => {
        set({ cart: initialCart });
      },
      
      getCartCount: () => {
        return get().cart.total_items;
      },
    }),
    {
      name: 'cart-storage',
      partialize: (state) => ({ cart: state.cart }),
    }
  )
);