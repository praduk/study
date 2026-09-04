export {};

declare global {
  interface Document {
    modelContext?: {
      registerTool: (
        tool: {
          name: string;
          title?: string;
          description: string;
          inputSchema: Record<string, unknown>;
          execute: (input: unknown) => unknown;
          annotations?: { readOnlyHint?: boolean; untrustedContentHint?: boolean };
        },
        options?: { signal?: AbortSignal },
      ) => void | Promise<void>;
    };
  }

  interface Window {
    EXCALIDRAW_ASSET_PATH?: string;
    MathJax?: {
      startup?: { promise?: Promise<unknown>; [key: string]: unknown };
      typesetClear?: (elements?: HTMLElement[]) => void;
      typesetPromise?: (elements?: HTMLElement[]) => Promise<unknown>;
      tex2svgPromise?: (tex: string, options?: { display?: boolean }) => Promise<HTMLElement>;
    } & Record<string, unknown>;
  }
}
