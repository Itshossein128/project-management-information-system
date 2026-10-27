/**
 * Common measurement units for building / construction activity logs.
 * Symbols are locale-agnostic (SI + typical site BoQ units).
 */
export const CONSTRUCTION_UNITS = [
  // Length
  "mm",
  "cm",
  "m",
  "km",
  "in",
  "ft",
  // Area
  "m²",
  "cm²",
  "km²",
  "ft²",
  "ha",
  // Volume
  "m³",
  "cm³",
  "L",
  "ft³",
  // Mass / weight
  "g",
  "kg",
  "t",
  "lb",
  // Count / packages
  "pcs",
  "set",
  "lot",
  "bag",
  // Time
  "h",
  "day",
  "week",
  "month",
  // Other
  "%",
  "LS",
  // Electrical & Mechanical Standard Units (Shiraz FILE 5 & 6)
  "متر طول",
  "شعله / نقطه",
  "دستگاه تابلو",
  "شاخه",
  "عدد",
  "دستگاه",
] as const;

export const ELECTRICAL_MEASUREMENT_UNITS = [
  "متر طول",
  "شعله / نقطه",
  "دستگاه تابلو",
  "شاخه",
  "عدد",
  "دستگاه",
] as const;

export type ConstructionUnit = (typeof CONSTRUCTION_UNITS)[number];

export const CONSTRUCTION_UNIT_OPTIONS = CONSTRUCTION_UNITS.map((unit) => ({
  value: unit,
  label: unit,
}));
