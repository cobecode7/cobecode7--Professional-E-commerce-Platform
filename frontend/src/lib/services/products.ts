/**
 * Product API Services
 */

import { api, PaginatedResponse } from '../api';
import {
  Product,
  ProductDetail,
  Category,
  ProductTag,
  ProductFilters,
} from '../../types/api';

export const productService = {
  // Products
  getProducts: async (filters?: ProductFilters): Promise<PaginatedResponse<Product>> => {
    return api.get('/products/', filters);
  },

  getProduct: async (slug: string): Promise<ProductDetail> => {
    return api.get(`/products/${slug}/`);
  },

  getFeaturedProducts: async (): Promise<Product[]> => {
    return api.get('/products/featured/');
  },

  searchProducts: async (searchData: {
    q?: string;
    category?: number;
    min_price?: number;
    max_price?: number;
    in_stock?: boolean;
    is_featured?: boolean;
    tags?: string[];
    ordering?: string;
  }): Promise<PaginatedResponse<Product>> => {
    return api.post('/products/search/', searchData);
  },

  getProductRecommendations: async (productId: number): Promise<Product[]> => {
    return api.get(`/products/${productId}/recommendations/`);
  },

  // Categories
  getCategories: async (): Promise<Category[]> => {
    return api.get('/products/categories/');
  },

  getCategory: async (slug: string): Promise<Category> => {
    return api.get(`/products/categories/${slug}/`);
  },

  getCategoryTree: async (): Promise<Category[]> => {
    return api.get('/products/categories/tree/');
  },

  // Tags
  getTags: async (): Promise<ProductTag[]> => {
    return api.get('/products/tags/');
  },

  // Inventory (admin only)
  getInventoryLogs: async (productId?: number): Promise<any[]> => {
    const params = productId ? { product: productId } : {};
    return api.get('/products/inventory/', params);
  },
};
