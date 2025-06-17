export interface Source {
  id: string;
  text: string;
}

export interface ApiResponse {
  answer: string;
  sources: Source[];
}

export interface ApiError {
  message: string;
  status?: number;
}

export class ApiClientError extends Error {
  status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
  }
}

export async function sendMessage(question: string): Promise<ApiResponse> {
  try {
    const apiBase = import.meta.env.VITE_API_BASE || "";
    const url = `${apiBase}/api/ask`;

    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({ question }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      let errorMessage = "Network error, please try again.";

      try {
        const errorData = JSON.parse(errorText);
        errorMessage = errorData.message || errorMessage;
      } catch {
        // Use default error message if JSON parsing fails
      }

      throw new ApiClientError(errorMessage, response.status);
    }

    const data = await response.json();

    // Validate response structure
    if (!data.answer || !Array.isArray(data.sources)) {
      throw new ApiClientError("Invalid response format from server");
    }

    return {
      answer: data.answer,
      sources: data.sources.map((source: any) => ({
        id: source.id || source.url || `source-${Date.now()}`,
        text: source.text || source.snippet || "Source information",
      })),
    };
  } catch (error) {
    if (error instanceof ApiClientError) {
      throw error;
    }

    // Handle network errors, timeouts, etc.
    if (error instanceof TypeError && error.message.includes("fetch")) {
      throw new ApiClientError(
        "Unable to connect to server. Please check your internet connection.",
      );
    }

    throw new ApiClientError("An unexpected error occurred. Please try again.");
  }
}

// Health check function for Cloud Run readiness
export async function healthCheck(): Promise<boolean> {
  try {
    const apiBase = import.meta.env.VITE_API_BASE || "";
    const response = await fetch(`${apiBase}/api/health`, {
      method: "GET",
    });
    return response.ok;
  } catch {
    return false;
  }
}
