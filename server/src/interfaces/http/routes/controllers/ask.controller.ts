import { Request, Response, NextFunction } from 'express';
import { askService } from '../../../../application/services/ask.service';
import { logger } from '../../../../core/logger.adapter';

export const askController = {
  async handleAsk(
    req: Request<{}, {}, { question: string }>,
    res: Response,
    next: NextFunction
  ) {
    try {
      const { answer, sources } = await askService.ask(req.body.question);
      res.json({ answer, sources });
    } catch (err) {
      logger.error('ask.controller failed', err);
      next(err);
    }
  },
};
