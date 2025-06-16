import { Router } from 'express';
import { z } from 'zod';
import { validateBody } from '../middleware/validation';
import { askController } from './controllers/ask.controller';

const AskSchema = z.object({ question: z.string().min(1) });
export const askRouter = Router().post(
  '/api/ask',
  validateBody(AskSchema),
  (req, res, next) => askController.handleAsk(req as any, res, next)
);
