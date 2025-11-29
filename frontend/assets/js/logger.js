/**
 * Environment-aware logging utility for FitMates V2
 * Provides production-safe logging with different log levels
 */

const LogLevel = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3,
  NONE: 4
};

class Logger {
  constructor() {
    // Determine environment - check for common production indicators
    this.isProduction = this.detectProduction();
    
    // Set log level based on environment
    this.logLevel = this.isProduction ? LogLevel.WARN : LogLevel.DEBUG;
    
    // Enable/disable console logging
    this.enabled = !this.isProduction || this.logLevel <= LogLevel.ERROR;
  }

  /**
   * Detect if running in production environment
   */
  detectProduction() {
    // Check hostname
    const hostname = window.location.hostname;
    if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname.includes('192.168')) {
      return false;
    }
    
    // Check for production domain patterns
    if (hostname.includes('fitmates') && !hostname.includes('dev') && !hostname.includes('staging')) {
      return true;
    }
    
    // Default to production-safe if uncertain
    return false;
  }

  /**
   * Format log message with timestamp
   */
  formatMessage(level, message, data) {
    const timestamp = new Date().toISOString();
    const prefix = `[${timestamp}] [${level}]`;
    
    if (data !== undefined) {
      return `${prefix} ${message}`;
    }
    return `${prefix} ${message}`;
  }

  /**
   * Check if should log based on level
   */
  shouldLog(level) {
    return this.enabled && level >= this.logLevel;
  }

  /**
   * Debug level logging - development only
   */
  debug(message, data) {
    if (this.shouldLog(LogLevel.DEBUG)) {
      const formatted = this.formatMessage('DEBUG', message, data);
      if (data !== undefined) {
        console.log(formatted, data);
      } else {
        console.log(formatted);
      }
    }
  }

  /**
   * Info level logging
   */
  info(message, data) {
    if (this.shouldLog(LogLevel.INFO)) {
      const formatted = this.formatMessage('INFO', message, data);
      if (data !== undefined) {
        console.info(formatted, data);
      } else {
        console.info(formatted);
      }
    }
  }

  /**
   * Warning level logging
   */
  warn(message, data) {
    if (this.shouldLog(LogLevel.WARN)) {
      const formatted = this.formatMessage('WARN', message, data);
      if (data !== undefined) {
        console.warn(formatted, data);
      } else {
        console.warn(formatted);
      }
    }
  }

  /**
   * Error level logging - always logs in production
   */
  error(message, error) {
    if (this.shouldLog(LogLevel.ERROR)) {
      const formatted = this.formatMessage('ERROR', message);
      console.error(formatted, error);
      
      // In production, you might want to send errors to a logging service
      if (this.isProduction) {
        this.sendToErrorService(message, error);
      }
    }
  }

  /**
   * Send errors to external logging service (placeholder)
   */
  sendToErrorService(message, error) {
    // TODO: Implement integration with error tracking service
    // Example: Sentry, LogRocket, etc.
    // This is a placeholder for future implementation
  }

  /**
   * Log API calls
   */
  apiCall(method, url, data) {
    this.debug(`API ${method} ${url}`, data);
  }

  /**
   * Log API responses
   */
  apiResponse(method, url, response) {
    this.debug(`API Response: ${method} ${url}`, response);
  }

  /**
   * Log API errors
   */
  apiError(method, url, error) {
    this.error(`API Error: ${method} ${url}`, error);
  }

  /**
   * Performance logging
   */
  performance(label, duration) {
    if (this.shouldLog(LogLevel.INFO)) {
      console.log(`⏱️ ${label}: ${duration}ms`);
    }
  }

  /**
   * User action logging (for analytics)
   */
  userAction(action, details) {
    this.info(`User Action: ${action}`, details);
    
    // Send to analytics service if in production
    if (this.isProduction && window.gtag) {
      // Google Analytics example
      window.gtag('event', action, details);
    }
  }
}

// Create singleton instance
const logger = new Logger();

// Export for use in other scripts
window.logger = logger;

// Provide shorthand functions
window.logDebug = (msg, data) => logger.debug(msg, data);
window.logInfo = (msg, data) => logger.info(msg, data);
window.logWarn = (msg, data) => logger.warn(msg, data);
window.logError = (msg, error) => logger.error(msg, error);