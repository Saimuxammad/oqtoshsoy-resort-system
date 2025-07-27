import React from 'react';
import { FunnelIcon } from '@heroicons/react/24/outline';
import { ROOM_TYPES } from '../../utils/constants';

export function RoomFilter({ filters, onChange }) {
  return (
    <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
      <div className="flex items-center gap-2 mb-3">
        <FunnelIcon className="h-5 w-5 text-gray-400" />
        <h3 className="font-medium text-gray-900">Filtrlash</h3>
      </div>

      <div className="space-y-3">
        {/* Holati */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Holati</label>
          <select
            value={filters.isAvailable ?? ''}
            onChange={(e) =>
              onChange({
                ...filters,
                isAvailable:
                  e.target.value === '' ? undefined : e.target.value === 'true',
              })
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">Barcha xonalar</option>
            <option value="true">Bo'sh xonalar</option>
            <option value="false">Band xonalar</option>
          </select>
        </div>

        {/* Xona turi */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Xona turi</label>
          <select
            value={filters.roomType || ''}
            onChange={(e) =>
              onChange({
                ...filters,
                roomType: e.target.value || undefined,
              })
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">Barcha turlar</option>
            {Object.entries(ROOM_TYPES).map(([key, value]) => (
              <option key={key} value={key}>
                {value}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}
