import { Geodata } from './geodata.component';

export function geodata(...args: ConstructorParameters<typeof Geodata>): Geodata {
  return new Geodata(...args);
}

export type { Geodata };