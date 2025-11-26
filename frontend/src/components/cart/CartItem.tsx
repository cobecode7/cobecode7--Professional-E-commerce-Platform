/**
 * Cart Item Component
 * Displays individual items in the shopping cart
 */

import Image from 'next/image';
import Link from 'next/link';
import { CartItem as CartItemType } from '../../types/api';
import { useUpdateCartItem, useRemoveFromCart } from '../../hooks/useShopping';
import { useState } from 'react';

interface CartItemProps {
  item: CartItemType;
}

export function CartItem({ item }: CartItemProps) {
  const [quantity, setQuantity] = useState(item.quantity);
  const updateCartItem = useUpdateCartItem();
  const removeFromCart = useRemoveFromCart();

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(price);
  };

  const handleQuantityChange = (newQuantity: number) => {
    if (newQuantity < 1) return;
    
    setQuantity(newQuantity);
    updateCartItem.mutate({
      itemId: item.id,
      quantity: newQuantity,
    });
  };

  const handleRemove = () => {
    removeFromCart.mutate(item.id);
  };

  return (
    <div className="flex items-center py-4 border-b border-gray-200">
      {/* Product Image */}
      <div className="flex-shrink-0">
        <Link href={`/products/${item.product.slug}`}>
          <div className="relative h-20 w-20">
            {item.product.primary_image ? (
              <Image
                src={item.product.primary_image.image}
                alt={item.product.name}
                fill
                className="object-cover rounded"
              />
            ) : (
              <div className="w-full h-full bg-gray-200 rounded flex items-center justify-center">
                <span className="text-gray-400 text-xs">No Image</span>
              </div>
            )}
          </div>
        </Link>
      </div>

      {/* Product Details */}
      <div className="flex-1 ml-4">
        <Link
          href={`/products/${item.product.slug}`}
          className="text-lg font-medium text-gray-900 hover:text-blue-600"
        >
          {item.product.name}
        </Link>
        
        {item.variant && (
          <p className="text-sm text-gray-600 mt-1">
            {item.variant.name}
            {item.variant.size && ` - Size: ${item.variant.size}`}
            {item.variant.color && ` - Color: ${item.variant.color}`}
          </p>
        )}
        
        <p className="text-sm text-gray-500 mt-1">
          SKU: {item.product.sku}
        </p>
        
        <div className="flex items-center justify-between mt-2">
          {/* Quantity Controls */}
          <div className="flex items-center">
            <button
              onClick={() => handleQuantityChange(quantity - 1)}
              disabled={quantity <= 1 || updateCartItem.isPending}
              className="p-1 rounded-md border border-gray-300 hover:bg-gray-50 disabled:opacity-50"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
              </svg>
            </button>
            
            <span className="mx-3 py-1 px-3 border border-gray-300 rounded-md min-w-[60px] text-center">
              {quantity}
            </span>
            
            <button
              onClick={() => handleQuantityChange(quantity + 1)}
              disabled={updateCartItem.isPending}
              className="p-1 rounded-md border border-gray-300 hover:bg-gray-50 disabled:opacity-50"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
            </button>
          </div>

          {/* Price and Remove */}
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-lg font-semibold text-gray-900">
                {formatPrice(item.total_price)}
              </p>
              <p className="text-sm text-gray-500">
                {formatPrice(item.unit_price)} each
              </p>
            </div>
            
            <button
              onClick={handleRemove}
              disabled={removeFromCart.isPending}
              className="text-red-600 hover:text-red-800 p-1 disabled:opacity-50"
              title="Remove item"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
