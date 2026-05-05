type Level = 'debug' | 'info' | 'warn' | 'error';

const IS_DEV = import.meta.env.DEV;

function log(level: Level, module: string, msg: string, data?: unknown): void {
  if (level === 'debug' && !IS_DEV) return;
  const ts = new Date().toISOString().replace('T', ' ').slice(0, 23);
  const prefix = `[${ts}] [${level.toUpperCase().padEnd(5)}] [${module}]`;
  if (data !== undefined) {
    console[level === 'debug' ? 'log' : level](`${prefix} ${msg}`, data);
  } else {
    console[level === 'debug' ? 'log' : level](`${prefix} ${msg}`);
  }
}

export const logger = {
  debug: (module: string, msg: string, data?: unknown) => log('debug', module, msg, data),
  info:  (module: string, msg: string, data?: unknown) => log('info',  module, msg, data),
  warn:  (module: string, msg: string, data?: unknown) => log('warn',  module, msg, data),
  error: (module: string, msg: string, data?: unknown) => log('error', module, msg, data),
  time: (module: string, label: string) => {
    const t0 = performance.now();
    return {
      end: (extra?: string) => {
        const ms = (performance.now() - t0).toFixed(1);
        log('info', module, `${label}${extra ? ` — ${extra}` : ''} [${ms}ms]`);
      },
    };
  },
};
