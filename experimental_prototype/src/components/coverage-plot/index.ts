import { CoveragePlot } from './coverage-plot.component';

export function coveragePlot(...args: ConstructorParameters<typeof CoveragePlot>): CoveragePlot {
  return new CoveragePlot(...args);
}

export type { CoveragePlot };
