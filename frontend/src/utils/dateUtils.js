// Utility functions for date/time formatting

/**
 * Format date to Indian Standard Time (IST)
 * @param {string|Date} dateString - Date string or Date object
 * @param {boolean} includeTime - Whether to include time (default: true)
 * @returns {string} Formatted date string in IST
 */
export const formatToIST = (dateString, includeTime = true) => {
  if (!dateString) return '-';
  
  const date = new Date(dateString);
  
  const options = {
    timeZone: 'Asia/Kolkata',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  };
  
  if (includeTime) {
    options.hour = '2-digit';
    options.minute = '2-digit';
    options.second = '2-digit';
    options.hour12 = true;
  }
  
  return date.toLocaleString('en-IN', options);
};

/**
 * Format time only to IST
 * @param {string|Date} dateString - Date string or Date object
 * @returns {string} Formatted time string in IST
 */
export const formatTimeToIST = (dateString) => {
  if (!dateString) return '-';
  
  const date = new Date(dateString);
  
  return date.toLocaleTimeString('en-IN', {
    timeZone: 'Asia/Kolkata',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true
  });
};

/**
 * Get current IST time
 * @returns {string} Current time in IST
 */
export const getCurrentIST = () => {
  return formatToIST(new Date());
};
