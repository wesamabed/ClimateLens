export const ENV = {
    Development: 'development',
    Production: 'production',
    Test: 'test',
  } as const;
  
  export type EnvName = (typeof ENV)[keyof typeof ENV];
  