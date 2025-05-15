import { Router } from 'express';
import type { Request, Response } from 'express';

export const rootRouter = Router().get(
  '/',
  (_req: Request, res: Response): void => {
    res.send('Hello ClimateLens');
  }
);
