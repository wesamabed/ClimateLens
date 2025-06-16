// server/src/application/services/ask.service.ts

import { genAiClient } from '../../infrastructure/ai/genai.client';
import { functionHandlerService, FunctionResult } from './functionHandler.service';
import { logger } from '../../core/logger.adapter';

export interface Source { id: string; text: string; }
export interface AskResult { answer: string; sources: Source[]; }

export class AskService {
  /**
   * 1) Let Gemini pick a tool (weather, emissions, etc.)
   * 2) If weather → return immediately
   * 3) Otherwise fetch numeric data + top-3 report excerpts
   * 4) Re-prompt Gemini to produce a single, Markdown-formatted answer
   */
  async ask(question: string): Promise<AskResult> {
    logger.info('[ask] start', { question });

    const systemPrompt = `
You are a climate assistant. Available tools:

• get_weather(place: string, date?: string, year?: number)  
  – Pass “date” (YYYY-MM-DD) for daily stats  
  – Pass “year” (YYYY) for an annual summary

• get_emissions(...)  
• get_report(...)  
• get_top_emitters(...)

When the user asks about weather, invoke get_weather with either its date or year.
`.trim();

    logger.debug('[ask] systemPrompt:', systemPrompt);
    const fnRes = await genAiClient.generateWithFunctions(question, systemPrompt);
    const fc = fnRes.functionCalls?.[0];

    if (fc?.name === 'get_weather') {
      logger.info('[ask] invoking get_weather', { args: fc.args });
      const wRes = await functionHandlerService.get_weather(fc.args as any);
      return { answer: wRes.answer, sources: wRes.sources };
    }

    // Otherwise: numeric or RAG
    if (!fc) {
      logger.warn('[ask] no function call → RAG fallback');
      return this.ragOnly(question);
    }

    let dataRes: FunctionResult;
    switch (fc.name) {
      case 'get_emissions':
        dataRes = await functionHandlerService.get_emissions(fc.args as any);
        break;
      case 'get_max_emissions':
        dataRes = await functionHandlerService.get_max_emissions(fc.args as any);
        break;
      case 'get_min_emissions':
        dataRes = await functionHandlerService.get_min_emissions(fc.args as any);
        break;
      case 'get_avg_emissions':
        dataRes = await functionHandlerService.get_avg_emissions(fc.args as any);
        break;
      case 'get_top_emitters':
        dataRes = await functionHandlerService.get_top_emitters(fc.args as any);
        break;
      case 'get_report':
        logger.info('[ask] get_report chosen → RAG fallback');
        return this.ragOnly(question);
      default:
        logger.warn('[ask] unknown function, RAG fallback', { function: fc.name });
        return this.ragOnly(question);
    }
    logger.debug('[ask] numeric data result:', dataRes);

    // Fetch top-3 report excerpts
    const reportRes = await functionHandlerService.get_report({ topic: question, k: 3 });
    logger.debug('[ask] report excerpts:', reportRes);

    // Build the prompt for the final answer
    const promptLines = [
      `Data: ${dataRes.answer}`,
      ...reportRes.sources.map(s => s.text),
      ``,
      `Question: ${question}`,
      `Answer:`
    ];
    const longPrompt = promptLines.join('\n\n');
    logger.info('[ask] finalPrompt length:', longPrompt.length);

    const formattingInstructions = `
You are a climate assistant. You will be given:

Data: <Data line>  
<excerpt 1>  
<excerpt 2>  
<excerpt 3>  

Use **only** this information—no outside facts—and output a **Markdown-formatted** answer:

1. **First sentence** with the number in **bold**.  
   - If the number came from an excerpt, append its bracketed citation (e.g. “[1]”).

2. **Context/Explanation**:
   - If any excerpt offers non-redundant insight, include a 1-3 item bullet list. Each bullet:
     - Summarizes *why* the excerpt matters
     - Ends with its bracketed citation
   - Otherwise, provide one concise closing sentence clarifying the result.

3. **References:**  
   - List all excerpts exactly as given, each prefixed by its bracketed citation.

Do **not** add any information beyond the Data line and the excerpts.
`.trim();

    const finalAnswer = await genAiClient.generateText(longPrompt, formattingInstructions);
    logger.info('[ask] finalAnswer received', { preview: finalAnswer.slice(0, 80) });

    return {
      answer: finalAnswer.trim(),
      sources: [...dataRes.sources, ...reportRes.sources],
    };
  }

  /** Pure-RAG fallback */
  private async ragOnly(question: string): Promise<AskResult> {
    const reportRes = await functionHandlerService.get_report({ topic: question, k: 5 });
    const prompt = [
      ...reportRes.sources.map(s => s.text),
      ``,
      `Question: ${question}`,
      `Answer:`
    ].join('\n\n');

    const answer = await genAiClient.generateText(
      prompt,
      'You are a climate assistant. Summarize these excerpts in Markdown and cite each by [number].'
    );
    return { answer: answer.trim(), sources: reportRes.sources };
  }
}

export const askService = new AskService();
