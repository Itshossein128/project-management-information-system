export interface TemperatureValidationOptions {
  isBlurOrSubmit?: boolean;
}

export interface TemperatureValidationResult {
  isValid: boolean;
  tempMinError: string | null;
  tempMaxError: string | null;
  parsedMin: string | null;
  parsedMax: string | null;
}

const INCOMPLETE_PATTERNS = ["-", "+", ".", "-.", "+."];

function evaluateField(
  raw: string,
  isBlurOrSubmit: boolean
): { error: string | null; parsed: string | null; isIncomplete: boolean } {
  const trimmed = raw.trim();
  if (trimmed === "") {
    return { error: null, parsed: null, isIncomplete: false };
  }

  if (INCOMPLETE_PATTERNS.includes(trimmed) || trimmed.endsWith(".")) {
    if (isBlurOrSubmit) {
      return { error: "invalid_number", parsed: null, isIncomplete: true };
    }
    return { error: null, parsed: null, isIncomplete: true };
  }

  const num = Number(trimmed);
  if (isNaN(num)) {
    return { error: "invalid_number", parsed: null, isIncomplete: false };
  }

  if (num < -40) {
    return { error: "min_value", parsed: trimmed, isIncomplete: false };
  }
  if (num > 60) {
    return { error: "max_value", parsed: trimmed, isIncomplete: false };
  }

  return { error: null, parsed: trimmed, isIncomplete: false };
}

export function validateTemperatures(
  tempMin: string,
  tempMax: string,
  options: TemperatureValidationOptions = { isBlurOrSubmit: true }
): TemperatureValidationResult {
  const isBlurOrSubmit = options.isBlurOrSubmit ?? true;

  const minEval = evaluateField(tempMin, isBlurOrSubmit);
  const maxEval = evaluateField(tempMax, isBlurOrSubmit);

  let tempMinError = minEval.error;
  let tempMaxError = maxEval.error;

  // Cross-field comparison if both are valid numbers and not incomplete
  if (
    !minEval.error &&
    !maxEval.error &&
    !minEval.isIncomplete &&
    !maxEval.isIncomplete &&
    minEval.parsed !== null &&
    maxEval.parsed !== null
  ) {
    const minVal = Number(minEval.parsed);
    const maxVal = Number(maxEval.parsed);
    if (maxVal < minVal) {
      tempMaxError = "temp_max_must_be_gte_temp_min";
    }
  }

  const hasErrors = Boolean(tempMinError || tempMaxError);
  const isIncomplete = minEval.isIncomplete || maxEval.isIncomplete;
  const isValid = !hasErrors && !isIncomplete;

  return {
    isValid,
    tempMinError,
    tempMaxError,
    parsedMin: minEval.parsed,
    parsedMax: maxEval.parsed,
  };
}
