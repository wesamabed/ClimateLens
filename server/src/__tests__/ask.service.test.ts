import { AskService } from '../application/services/ask.service';
import { genAiClient } from '../infrastructure/ai/genai.client';
import { functionHandlerService, FunctionResult } from '../application/services/functionHandler.service';

jest.mock('../infrastructure/ai/genai.client');
jest.mock('../application/services/functionHandler.service');

const mockedGenAi = genAiClient as jest.Mocked<typeof genAiClient>;
const mockedFnSvc = functionHandlerService as jest.Mocked<typeof functionHandlerService>;

describe('AskService', () => {
  let svc: AskService;

  beforeEach(() => {
    svc = new AskService();
    jest.resetAllMocks();
  });

  it('… annual weather summary via get_weather(...)', async () => {
    // 1) Gemini picks get_weather with a year-only
    mockedGenAi.generateWithFunctions.mockResolvedValueOnce({
      functionCalls: [{
        name: 'get_weather',
        args: { place: 'Berlin', year: 2020 }
      }]
    } as any);

    // 2) Mock the public get_weather(...) to return your summary result
    const summaryRes: FunctionResult = {
      answer: 'In **2020**, average **12.3°C**, prcp **500 mm**.',
      sources: [{ id: 'w2', text: 'Station …, 2020: avgTemp=12.3°C, prcp=500 mm' }]
    };
    mockedFnSvc.get_weather.mockResolvedValueOnce(summaryRes);

    // 3) Call
    const result = await svc.ask('What was the weather in Berlin in 2020?');

    // 4) Assertions
    expect(mockedGenAi.generateWithFunctions).toHaveBeenCalled();
    expect(mockedFnSvc.get_weather).toHaveBeenCalledWith({ place: 'Berlin', year: 2020 });
    expect(result.answer).toBe(summaryRes.answer);
    expect(result.sources).toEqual(summaryRes.sources);
  });
});
