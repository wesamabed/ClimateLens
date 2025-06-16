import { AskService, AskResult } from '../application/services/ask.service';
import { functionHandlerService } from '../application/services/functionHandler.service';
import { genAiClient } from '../infrastructure/ai/genai.client';
import { FunctionResult } from '../application/services/functionHandler.service';

describe('AskService (unit)', () => {
  let svc: AskService;

  beforeEach(() => {
    jest.clearAllMocks();
    svc = new AskService();
  });

  it('routes a year-only weather question into get_weather', async () => {
    // 1) stub the LLM to call get_weather(place, date)
    jest
      .spyOn(genAiClient, 'generateWithFunctions')
      .mockResolvedValue({ functionCalls: [{ name: 'get_weather', args: { place: 'Tel Aviv', date: '2020' } }] } as any);

    // 2) spy on functionHandlerService.get_weather
    jest
      .spyOn(functionHandlerService, 'get_weather')
      .mockResolvedValue({ answer: 'YEAR SUMMARY', sources: [] });

    const res: AskResult = await svc.ask('Weather in Tel Aviv in 2020?');

    expect(functionHandlerService.get_weather).toHaveBeenCalledWith({ place: 'Tel Aviv', date: '2020' });
    expect(res.answer).toBe('YEAR SUMMARY');
    expect(res.sources).toEqual([]);
  });
});
