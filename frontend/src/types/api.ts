/**
 * TypeScript Types for API Integration
 */

// User & Authentication Types
export interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
  date_of_birth?: string;
  is_email_verified: boolean;
  full_name: string;
  date_joined: string;
  last_login?: string;
}

export interface UserProfile {
  user: User;
  bio: string;
  avatar?: string;
  website?: string;
  location?: string;
  marketing_emails: boolean;
  sms_notifications: boolean;
  created_at: string;
  updated_at: string;
}

export interface Address {
  id: number;
  type: 'shipping' | 'billing' | 'both';
  first_name: string;
  last_name: string;
  company?: string;
  address_line_1: string;
  address_line_2?: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  is_default: boolean;
  full_address: string;
  created_at: string;
  updated_at: string;
}

// Auth API Types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
  password: string;
  password_confirm: string;
}

export interface AuthResponse {
  user: User;
  token: string;
  message: string;
}

// Product Types
export interface ProductTag {
  id: number;
  name: string;
  slug: string;
}

export interface ProductImage {
  id: number;
  image: string;
  alt_text: string;
  is_primary: boolean;
  sort_order: number;
}

export interface ProductVariant {
  id: number;
  name: string;
  sku: string;
  size?: string;
  color?: string;
  material?: string;
  price?: number;
  sale_price?: number;
  current_price: number;
  stock_quantity: number;
  is_active: boolean;
  is_in_stock: boolean;
  image?: string;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string;
  image?: string;
  parent?: number;
  full_path: string;
  product_count: number;
  children?: Category[];
  is_active: boolean;
  sort_order: number;
}

export interface Product {
  id: number;
  name: string;
  slug: string;
  sku: string;
  description?: string;
  short_description?: string;
  price: number;
  sale_price?: number;
  current_price: number;
  discount_percentage: number;
  is_in_stock: boolean;
  is_featured: boolean;
  category_name: string;
  primary_image?: ProductImage;
  tags: ProductTag[];
  view_count: number;
  created_at: string;
}

export interface ProductDetail extends Product {
  product_type: 'simple' | 'variable' | 'digital';
  category: Category;
  stock_status: 'in_stock' | 'out_of_stock' | 'on_backorder';
  manage_stock: boolean;
  stock_quantity: number;
  low_stock_threshold: number;
  is_low_stock: boolean;
  weight?: number;
  length?: number;
  width?: number;
  height?: number;
  meta_title?: string;
  meta_description?: string;
  is_active: boolean;
  is_digital: boolean;
  images: ProductImage[];
  variants: ProductVariant[];
  updated_at: string;
}

// Cart & Order Types
export interface CartItem {
  id: number;
  product: Product;
  variant?: ProductVariant;
  quantity: number;
  unit_price: number;
  total_price: number;
  created_at: string;
  updated_at: string;
}

export interface Cart {
  id: number;
  items: CartItem[];
  total_items: number;
  subtotal: number;
  total_weight: number;
  created_at: string;
  updated_at: string;
}

export interface AddToCartRequest {
  product_id: number;
  variant_id?: number;
  quantity: number;
}

export interface OrderItem {
  id: number;
  product_name: string;
  product_sku: string;
  variant_name?: string;
  quantity: number;
  unit_price: number;
  total_price: number;
}

export interface Payment {
  id: string;
  payment_method: string;
  amount: number;
  currency: string;
  status: string;
  gateway_transaction_id?: string;
  card_last_four?: string;
  card_brand?: string;
  is_successful: boolean;
  can_be_refunded: boolean;
  refund_amount: number;
  created_at: string;
  processed_at?: string;
}

export interface Order {
  id: string;
  order_number: string;
  status: 'pending' | 'paid' | 'processing' | 'shipped' | 'delivered' | 'cancelled' | 'refunded';
  shipping_status: 'pending' | 'preparing' | 'shipped' | 'in_transit' | 'delivered' | 'returned';
  items: OrderItem[];
  payments: Payment[];
  billing_first_name: string;
  billing_last_name: string;
  billing_email: string;
  billing_address: string;
  shipping_address: string;
  subtotal: number;
  shipping_cost: number;
  tax_amount: number;
  discount_amount: number;
  total_amount: number;
  total_items: number;
  can_be_cancelled: boolean;
  is_paid: boolean;
  tracking_number?: string;
  shipping_method?: string;
  estimated_delivery_date?: string;
  customer_notes?: string;
  created_at: string;
  updated_at: string;
  shipped_at?: string;
  delivered_at?: string;
}

export interface CreateOrderRequest {
  billing_first_name: string;
  billing_last_name: string;
  billing_email: string;
  billing_phone?: string;
  billing_address_line_1: string;
  billing_address_line_2?: string;
  billing_city: string;
  billing_state: string;
  billing_postal_code: string;
  billing_country: string;
  shipping_first_name: string;
  shipping_last_name: string;
  shipping_address_line_1: string;
  shipping_address_line_2?: string;
  shipping_city: string;
  shipping_state: string;
  shipping_postal_code: string;
  shipping_country: string;
  customer_notes?: string;
  shipping_method?: string;
}

// Shipping & Discounts
export interface ShippingMethod {
  id: number;
  name: string;
  description: string;
  base_cost: number;
  cost_per_kg: number;
  min_delivery_days: number;
  max_delivery_days: number;
  min_order_amount: number;
  max_weight?: number;
  is_active: boolean;
}

export interface Discount {
  id: number;
  code: string;
  name: string;
  description: string;
  discount_type: 'percentage' | 'fixed_amount' | 'free_shipping';
  value: number;
  minimum_order_amount: number;
  maximum_discount_amount?: number;
  valid_from: string;
  valid_until?: string;
  is_active: boolean;
}

export interface ApplyDiscountRequest {
  code: string;
  order_total: number;
}

export interface DiscountResponse {
  discount: Discount;
  discount_amount: number;
  new_total: number;
}

// Search & Filter Types
export interface ProductFilters {
  q?: string;
  category?: number;
  min_price?: number;
  max_price?: number;
  in_stock?: boolean;
  is_featured?: boolean;
  tags?: string[];
  ordering?: string;
  page?: number;
  page_size?: number;
}

export interface CheckoutCalculation {
  subtotal: number;
  shipping_cost: number;
  tax_amount: number;
  discount_amount: number;
  total: number;
  cart_items: number;
}
