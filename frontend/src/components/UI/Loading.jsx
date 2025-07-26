import React from 'react';

export function Loading({ text = "Yuklanmoqda..." }) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <div className="relative">
        <div className="h-12 w-12 rounded-full border-4 border-gray-200"></div>
        <div className="absolute top-0 h-12 w-12 rounded-full border-4 border-primary-600 border-t-transparent animate-spin"></div>
      </div>
      <p className="mt-4 text-sm text-gray-600">{text}</p>
    </div>
  );
}