/**
 * Product Card Component
 * Displays product information in a card layout
 */

import Image from 'next/image';
import Link from 'next/link';
import { Product } from '../../types/api';
import { useAddToCart } from '../../hooks/useShopping';

interface ProductCardProps {
  product: Product;
}

export function ProductCard({ product }: ProductCardProps) {
  const addToCartMutation = useAddToCart();

  const handleAddToCart = (e: React.MouseEvent) => {
    e.preventDefault(); // Prevent navigation when clicking the button
    
    addToCartMutation.mutate({
      product_id: product.id,
      quantity: 1,
    });
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(price);
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-200">
      <Link href={`/products/${product.slug}`}>
        <div className="relative h-64 w-full">
          {product.primary_image ? (
            <Image
              src={product.primary_image.image}
              alt={product.primary_image.alt_text || product.name}
              fill
              className="object-cover"
            />
          ) : (
            <div className="w-full h-full bg-gray-200 flex items-center justify-center">
              <span className="text-gray-400">No Image</span>
            </div>
          )}
          
          {/* Discount Badge */}
          {product.discount_percentage > 0 && (
            <div className="absolute top-2 left-2 bg-red-500 text-white px-2 py-1 rounded text-sm font-semibold">
              -{product.discount_percentage}%
            </div>
          )}
          
          {/* Featured Badge */}
          {product.is_featured && (
            <div className="absolute top-2 right-2 bg-yellow-500 text-white px-2 py-1 rounded text-sm font-semibold">
              Featured
            </div>
          )}
        </div>
      </Link>

      <div className="p-4">
        <Link href={`/products/${product.slug}`}>
          <h3 className="text-lg font-semibold text-gray-900 hover:text-blue-600 transition-colors">
            {product.name}
          </h3>
        </Link>
        
        <p className="text-gray-600 text-sm mt-1 line-clamp-2">
          {product.short_description}
        </p>
        
        {/* Category */}
        <p className="text-xs text-gray-500 mt-2">
          {product.category_name}
        </p>
        
        {/* Price */}
        <div className="flex items-center justify-between mt-3">
          <div className="flex items-center space-x-2">
            <span className="text-xl font-bold text-gray-900">
              {formatPrice(product.current_price)}
            </span>
            {product.sale_price && product.sale_price < product.price && (
              <span className="text-sm text-gray-500 line-through">
                {formatPrice(product.price)}
              </span>
            )}
          </div>
          
          {/* Stock Status */}
          <span
            className={`text-xs px-2 py-1 rounded ${
              product.is_in_stock
                ? 'bg-green-100 text-green-800'
                : 'bg-red-100 text-red-800'
            }`}
          >
            {product.is_in_stock ? 'In Stock' : 'Out of Stock'}
          </span>
        </div>
        
        {/* Tags */}
        {product.tags && product.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {product.tags.slice(0, 3).map((tag) => (
              <span
                key={tag.id}
                className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded"
              >
                {tag.name}
              </span>
            ))}
          </div>
        )}
        
        {/* Add to Cart Button */}
        <button
          onClick={handleAddToCart}
          disabled={!product.is_in_stock || addToCartMutation.isPending}
          className="w-full mt-4 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors duration-200"
        >
          {addToCartMutation.isPending
            ? 'Adding...'
            : product.is_in_stock
            ? 'Add to Cart'
            : 'Out of Stock'}
        </button>
      </div>
    </div>
  );
}
