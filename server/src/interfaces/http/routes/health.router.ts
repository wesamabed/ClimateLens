import { Router } from 'express';
import type { Request, Response } from 'express';

export const healthRouter = Router().get(
  '/health',
  (_req: Request, res: Response): void => {
    res.json({ status: 'ok' });
  }
);
