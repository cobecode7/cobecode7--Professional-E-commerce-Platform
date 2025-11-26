/**
 * Product React Query Hooks
 */

import { useQuery, useInfiniteQuery } from '@tanstack/react-query';
import { productService } from '../lib/services/products';
import {
  Product,
  ProductDetail,
  Category,
  ProductTag,
  ProductFilters,
} from '../types/api';

// Query Keys
export const PRODUCT_KEYS = {
  products: ['products'] as const,
  productsList: (filters?: ProductFilters) => ['products', 'list', filters] as const,
  product: (slug: string) => ['products', 'detail', slug] as const,
  featuredProducts: ['products', 'featured'] as const,
  recommendations: (id: number) => ['products', 'recommendations', id] as const,
  categories: ['products', 'categories'] as const,
  categoryTree: ['products', 'categories', 'tree'] as const,
  category: (slug: string) => ['products', 'category', slug] as const,
  tags: ['products', 'tags'] as const,
  search: (query: any) => ['products', 'search', query] as const,
};

// Product Hooks
export const useProducts = (filters?: ProductFilters) => {
  return useQuery({
    queryKey: PRODUCT_KEYS.productsList(filters),
    queryFn: () => productService.getProducts(filters),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

export const useInfiniteProducts = (filters?: ProductFilters) => {
  return useInfiniteQuery({
    queryKey: ['products', 'infinite', filters],
    queryFn: ({ pageParam = 1 }) => 
      productService.getProducts({ ...filters, page: pageParam }),
    getNextPageParam: (lastPage, allPages) => {
      if (lastPage.results.length === 0) return undefined;
      return allPages.length + 1;
    },
    initialPageParam: 1,
    staleTime: 2 * 60 * 1000,
  });
};

export const useProduct = (slug: string) => {
  return useQuery({
    queryKey: PRODUCT_KEYS.product(slug),
    queryFn: () => productService.getProduct(slug),
    enabled: !!slug,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useFeaturedProducts = () => {
  return useQuery({
    queryKey: PRODUCT_KEYS.featuredProducts,
    queryFn: productService.getFeaturedProducts,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
};

export const useProductRecommendations = (productId: number) => {
  return useQuery({
    queryKey: PRODUCT_KEYS.recommendations(productId),
    queryFn: () => productService.getProductRecommendations(productId),
    enabled: !!productId,
    staleTime: 15 * 60 * 1000, // 15 minutes
  });
};

export const useProductSearch = (searchQuery: any) => {
  return useQuery({
    queryKey: PRODUCT_KEYS.search(searchQuery),
    queryFn: () => productService.searchProducts(searchQuery),
    enabled: Object.keys(searchQuery).length > 0,
    staleTime: 1 * 60 * 1000, // 1 minute
  });
};

// Category Hooks
export const useCategories = () => {
  return useQuery({
    queryKey: PRODUCT_KEYS.categories,
    queryFn: productService.getCategories,
    staleTime: 30 * 60 * 1000, // 30 minutes
  });
};

export const useCategoryTree = () => {
  return useQuery({
    queryKey: PRODUCT_KEYS.categoryTree,
    queryFn: productService.getCategoryTree,
    staleTime: 30 * 60 * 1000, // 30 minutes
  });
};

export const useCategory = (slug: string) => {
  return useQuery({
    queryKey: PRODUCT_KEYS.category(slug),
    queryFn: () => productService.getCategory(slug),
    enabled: !!slug,
    staleTime: 15 * 60 * 1000, // 15 minutes
  });
};

// Tag Hooks
export const useTags = () => {
  return useQuery({
    queryKey: PRODUCT_KEYS.tags,
    queryFn: productService.getTags,
    staleTime: 30 * 60 * 1000, // 30 minutes
  });
};
