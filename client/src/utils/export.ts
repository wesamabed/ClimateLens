import { saveAs } from "file-saver";
import { Message } from "../App";

export interface ExportOptions {
  format: "json" | "txt";
  includeTimestamps?: boolean;
  includeSources?: boolean;
}

export function exportChat(
  messages: Message[],
  options: ExportOptions = { format: "txt" },
): void {
  const timestamp = new Date().toISOString().split("T")[0];
  const filename = `climateLens-chat-${timestamp}`;

  if (options.format === "json") {
    exportAsJSON(messages, filename);
  } else {
    exportAsText(messages, filename, options);
  }
}

function exportAsJSON(messages: Message[], filename: string): void {
  const exportData = {
    exportedAt: new Date().toISOString(),
    messageCount: messages.length,
    messages: messages.map((msg) => ({
      id: msg.id,
      role: msg.role,
      text: msg.text,
      timestamp: msg.timestamp,
      sources: msg.sources || [],
    })),
  };

  const blob = new Blob([JSON.stringify(exportData, null, 2)], {
    type: "application/json;charset=utf-8",
  });

  saveAs(blob, `${filename}.json`);
}

function exportAsText(
  messages: Message[],
  filename: string,
  options: ExportOptions,
): void {
  let content = "ClimateLens Chat Export\n";
  content += "=".repeat(25) + "\n";
  content += `Exported: ${new Date().toLocaleString()}\n`;
  content += `Messages: ${messages.length}\n\n`;

  messages.forEach((message) => {
    const role = message.role === "user" ? "You" : "ClimateLens";
    content += `${role}:\n`;

    if (options.includeTimestamps) {
      content += `[${new Date(message.timestamp).toLocaleString()}]\n`;
    }

    content += `${message.text}\n`;

    if (
      options.includeSources &&
      message.sources &&
      message.sources.length > 0
    ) {
      content += "\nSources:\n";
      message.sources.forEach((source, sourceIndex) => {
        content += `${sourceIndex + 1}. ${source.text}\n`;
        if (isValidUrl(source.id)) {
          content += `   URL: ${source.id}\n`;
        }
      });
    }

    content += "\n" + "-".repeat(50) + "\n\n";
  });

  const blob = new Blob([content], {
    type: "text/plain;charset=utf-8",
  });

  saveAs(blob, `${filename}.txt`);
}

function isValidUrl(string: string): boolean {
  try {
    new URL(string);
    return true;
  } catch {
    return false;
  }
}

export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return true;
    } else {
      // Fallback for older browsers
      const textArea = document.createElement("textarea");
      textArea.value = text;
      textArea.style.position = "fixed";
      textArea.style.left = "-999999px";
      textArea.style.top = "-999999px";
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      const success = document.execCommand("copy");
      textArea.remove();
      return success;
    }
  } catch (error) {
    console.error("Failed to copy to clipboard:", error);
    return false;
  }
}
