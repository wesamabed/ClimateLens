// server/src/infrastructure/ai/genai.client.ts
import {
  GoogleGenAI,
  FunctionCallingConfigMode,
  FunctionDeclaration,
} from '@google/genai';
import { config } from '../../core/config.factory';
import {
  getEmissionsFunction,
  getReportFunction,
  getMaxEmissionsFunction,
  getMinEmissionsFunction,
  getAvgEmissionsFunction,
  getTopEmittersFunction,
  getWeatherFunction,

} from './functionDeclarations';

export class GenAIClient {
  private ai: GoogleGenAI;
  private tools: FunctionDeclaration[];

  constructor() {
    const opts: any = {};
    if (config.GOOGLE_GENAI_USE_VERTEXAI) {
      opts.vertexai = true;
      opts.project   = config.GOOGLE_CLOUD_PROJECT;
      opts.location  = config.GOOGLE_CLOUD_LOCATION;
    } else {
      opts.apiKey = config.GEMINI_API_KEY;
    }

    this.ai = new GoogleGenAI(opts);
    this.tools = [
      getEmissionsFunction,
      getReportFunction,
      getMaxEmissionsFunction,
      getMinEmissionsFunction,
      getAvgEmissionsFunction,
      getTopEmittersFunction,
      getWeatherFunction,
    ];
  }

  /** 
   * Phase 1: let Gemini choose & call one numeric function 
   */
  async generateWithFunctions(userText: string, systemText?: string) {
    const prompt = systemText ? `${systemText}\n\n${userText}` : userText;
    return this.ai.models.generateContent({
      model: 'gemini-2.0-flash',
      contents: prompt,
      config: {
        toolConfig: {
          functionCallingConfig: { mode: FunctionCallingConfigMode.ANY }
        },
        tools: [{ functionDeclarations: this.tools }],
      },
    });
  }

  /**
   * Phase 3: plain-text generation (no tools)
   */
  async generateText(prompt: string, systemText?: string): Promise<string> {
    const full = systemText ? `${systemText}\n\n${prompt}` : prompt;
    const res = await this.ai.models.generateContent({
      model: 'gemini-2.0-flash',
      contents: full,
    });
    return res.text || '';
  }
}

export const genAiClient = new GenAIClient();
