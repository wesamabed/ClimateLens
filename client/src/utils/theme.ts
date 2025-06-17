export type Theme = "light" | "dark";

export interface ThemeColors {
  primary: string;
  primaryAlpha: string;
  background: {
    primary: string;
    secondary: string;
    header: string;
    input: string;
    inputField: string;
  };
  text: {
    primary: string;
    secondary: string;
    header: string;
  };
  border: string;
  bubbles: {
    user: {
      background: string;
      text: string;
    };
    assistant: {
      background: string;
      text: string;
    };
  };
  scrollbar: {
    thumb: string;
    thumbHover: string;
  };
  error: {
    background: string;
    border: string;
    text: string;
  };
  success: {
    background: string;
    border: string;
    text: string;
  };
}

export const lightTheme: ThemeColors = {
  primary: "#059669",
  primaryAlpha: "rgba(5, 150, 105, 0.1)",
  background: {
    primary: "#ffffff",
    secondary: "#f8f9fa",
    header: "rgba(255, 255, 255, 0.9)",
    input: "rgba(255, 255, 255, 0.9)",
    inputField: "#ffffff",
  },
  text: {
    primary: "#1a1a1a",
    secondary: "#6b7280",
    header: "#1a1a1a",
  },
  border: "#e5e7eb",
  bubbles: {
    user: {
      background: "#059669",
      text: "#ffffff",
    },
    assistant: {
      background: "#ffffff",
      text: "#1a1a1a",
    },
  },
  scrollbar: {
    thumb: "rgba(0, 0, 0, 0.2)",
    thumbHover: "rgba(0, 0, 0, 0.3)",
  },
  error: {
    background: "#fef2f2",
    border: "#fca5a5",
    text: "#dc2626",
  },
  success: {
    background: "#f0fdf4",
    border: "#86efac",
    text: "#16a34a",
  },
};

export const darkTheme: ThemeColors = {
  primary: "#10b981",
  primaryAlpha: "rgba(16, 185, 129, 0.1)",
  background: {
    primary: "#0f172a",
    secondary: "#1e293b",
    header: "rgba(15, 23, 42, 0.9)",
    input: "rgba(15, 23, 42, 0.9)",
    inputField: "#1e293b",
  },
  text: {
    primary: "#f1f5f9",
    secondary: "#94a3b8",
    header: "#f1f5f9",
  },
  border: "#334155",
  bubbles: {
    user: {
      background: "#10b981",
      text: "#ffffff",
    },
    assistant: {
      background: "#1e293b",
      text: "#f1f5f9",
    },
  },
  scrollbar: {
    thumb: "rgba(255, 255, 255, 0.2)",
    thumbHover: "rgba(255, 255, 255, 0.3)",
  },
  error: {
    background: "#450a0a",
    border: "#dc2626",
    text: "#fca5a5",
  },
  success: {
    background: "#052e16",
    border: "#16a34a",
    text: "#86efac",
  },
};

export function applyTheme(theme: Theme): void {
  const colors = theme === "light" ? lightTheme : darkTheme;
  const root = document.documentElement;

  // Apply CSS variables
  root.style.setProperty("--primary-color", colors.primary);
  root.style.setProperty("--primary-color-alpha", colors.primaryAlpha);

  // Background colors
  root.style.setProperty("--bg-primary", colors.background.primary);
  root.style.setProperty("--bg-secondary", colors.background.secondary);
  root.style.setProperty("--header-bg", colors.background.header);
  root.style.setProperty("--input-bg", colors.background.input);
  root.style.setProperty("--input-field-bg", colors.background.inputField);

  // Text colors
  root.style.setProperty("--text-primary", colors.text.primary);
  root.style.setProperty("--text-secondary", colors.text.secondary);
  root.style.setProperty("--header-text", colors.text.header);

  // Border
  root.style.setProperty("--border-color", colors.border);

  // Bubble colors
  root.style.setProperty("--user-bubble-bg", colors.bubbles.user.background);
  root.style.setProperty("--user-bubble-text", colors.bubbles.user.text);
  root.style.setProperty(
    "--assistant-bubble-bg",
    colors.bubbles.assistant.background,
  );
  root.style.setProperty(
    "--assistant-bubble-text",
    colors.bubbles.assistant.text,
  );

  // Scrollbar
  root.style.setProperty("--scrollbar-thumb", colors.scrollbar.thumb);
  root.style.setProperty(
    "--scrollbar-thumb-hover",
    colors.scrollbar.thumbHover,
  );

  // Error and success states
  root.style.setProperty("--error-bg", colors.error.background);
  root.style.setProperty("--error-border", colors.error.border);
  root.style.setProperty("--error-text", colors.error.text);
  root.style.setProperty("--success-bg", colors.success.background);
  root.style.setProperty("--success-border", colors.success.border);
  root.style.setProperty("--success-text", colors.success.text);

  // Set theme attribute
  root.setAttribute("data-theme", theme);
}

export function getStoredTheme(): Theme {
  const stored = localStorage.getItem("climateLens_theme");
  return stored === "dark" ? "dark" : "light";
}

export function storeTheme(theme: Theme): void {
  localStorage.setItem("climateLens_theme", theme);
}
