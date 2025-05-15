import pino from 'pino';
import pretty from 'pino-pretty';
import { config } from './config.factory';
import { LoggingPort } from './logging.port';

const stream =
  config.NODE_ENV === 'production' ? undefined : pretty({ colorize: true });

const base = pino(
  { level: config.NODE_ENV === 'production' ? 'info' : 'debug' },
  stream as any
);

/** Adapter: Pino implements LoggingPort */
export const logger: LoggingPort = {
  debug: (m, meta) => base.debug(meta, m),
  info:  (m, meta) => base.info (meta, m),
  warn:  (m, meta) => base.warn (meta, m),
  error: (m, meta) => base.error(meta, m),
};
