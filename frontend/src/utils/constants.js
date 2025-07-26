export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const ROOM_TYPES = {
  STANDARD_2: "2 o'rinli standart",
  STANDARD_4: "4 o'rinli standart",
  LUX_2: "2 o'rinli lyuks",
  VIP_SMALL_4: "4 o'rinli kichik VIP",
  VIP_BIG_4: "4 o'rinli katta VIP",
  APARTMENT_4: "4 o'rinli apartament",
  COTTAGE_6: "Kottedj (6 kishi uchun)",
  PRESIDENT_8: "Prezident apartamenti (8 kishi uchun)"
};

export const ROOM_STATUS = {
  AVAILABLE: 'Bo\'sh',
  OCCUPIED: 'Band'
};

export const DATE_FORMAT = 'd-MMM';