export function getErrorMessage(error, defaultMessage = "An error occurred") {
  const detail = error?.response?.data?.detail;
  return typeof detail === "string" ? detail : defaultMessage;
}