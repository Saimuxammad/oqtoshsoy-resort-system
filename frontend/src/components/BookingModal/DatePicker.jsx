import React from 'react';
import ReactDatePicker from 'react-datepicker';
import { uz } from 'date-fns/locale';
import "react-datepicker/dist/react-datepicker.css";

export function DatePicker({ label, selected, onChange, minDate, ...props }) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
      </label>
      <ReactDatePicker
        selected={selected}
        onChange={onChange}
        locale={uz}
        dateFormat="dd.MM.yyyy"
        minDate={minDate}
        className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
        {...props}
      />
    </div>
  );
}