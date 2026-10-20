/** Filename helpers for MSP/P6 schedule import routing (no API client imports). */

export function isP6File(file: { name: string }): boolean {
  return file.name.toLowerCase().endsWith(".xer");
}

/** Microsoft Project XML or native MPP (MSP-family APIs). */
export function isMspFamilyFile(file: { name: string }): boolean {
  const lower = file.name.toLowerCase();
  return lower.endsWith(".xml") || lower.endsWith(".mpp");
}

export function isScheduleImportFile(file: { name: string }): boolean {
  return isP6File(file) || isMspFamilyFile(file);
}
