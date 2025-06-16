import { GenAIClient } from '../infrastructure/ai/genai.client';
import { GoogleGenAI, FunctionCallingConfigMode } from '@google/genai';
import * as fns from '../infrastructure/ai/functionDeclarations';

jest.mock('@google/genai');
jest.mock('../core/config.factory', () => ({
  config: {
    GOOGLE_GENAI_USE_VERTEXAI: false,
    GEMINI_API_KEY: 'abc',
    GOOGLE_CLOUD_PROJECT: 'proj',
    GOOGLE_CLOUD_LOCATION: 'loc',
  },
}));

describe('GenAIClient', () => {
  let client: GenAIClient;
  let mockGenerateContent: jest.Mock;

  beforeEach(() => {
    // reset the mock class
    (GoogleGenAI as jest.Mock).mockClear();

    // 1) Construct your client (this calls new GoogleGenAI(opts))
    client = new GenAIClient();

    // 2) Grab that single mocked instance, ensure it has a `models` map,
    //    then stub out generateContent
    const giInstance = (GoogleGenAI as jest.Mock).mock.instances[0] as any;
    if (!giInstance.models) {
      giInstance.models = {};
    }
    mockGenerateContent = (giInstance.models.generateContent = jest.fn());
  });

  it('generateWithFunctions bundles prompt and tools correctly', async () => {
    mockGenerateContent.mockResolvedValue({ functionCalls: [], text: '' });
    await client.generateWithFunctions('hey', 'sys');
    expect(mockGenerateContent).toHaveBeenCalledWith(
      expect.objectContaining({
        model: 'gemini-2.0-flash',
        contents: 'sys\n\nhey',
        config: expect.objectContaining({
          toolConfig: {
            functionCallingConfig: { mode: FunctionCallingConfigMode.ANY },
          },
          tools: [
            {
              functionDeclarations: expect.arrayContaining([
                fns.getEmissionsFunction,
                fns.getReportFunction,
                fns.getWeatherFunction,
              ]),
            },
          ],
        }),
      })
    );
  });

  it('generateText returns res.text or empty string', async () => {
    mockGenerateContent.mockResolvedValue({ text: 'hello' });
    await expect(client.generateText('p', 's')).resolves.toBe('hello');

    mockGenerateContent.mockResolvedValue({});
    await expect(client.generateText('p2')).resolves.toBe('');
  });
});
