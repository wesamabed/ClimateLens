import { Request, Response, NextFunction } from 'express';
import { logger } from '../../../core/logger.adapter';

export function errorHandler(
  err: unknown,
  _req: Request,
  res: Response,
  _next: NextFunction
): void {
  logger.error('Unhandled error', err);
  const status = (err as any).statusCode ?? 500;
  const message = (err as any).message ?? 'Internal Server Error';
  res.status(status).json({ error: message });
}
