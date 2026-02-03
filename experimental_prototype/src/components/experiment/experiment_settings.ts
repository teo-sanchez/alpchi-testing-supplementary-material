import type { BatchPrediction } from '@marcellejs/core';
import type { Model, Component, Instance } from '@marcellejs/core';
import type { DataStore } from '@marcellejs/core';
import type { Dataset } from '@marcellejs/core';

function isTitle(x: Component | Component[] | string): x is string {
  return typeof x === 'string';
}

function isComponentArray(x: Component | Component[] | string): x is Component[] {
  return Array.isArray(x);
}

export class ExperimentSettings {
  name = 'settings';
  components: Array<Component | Component[] | string> = [];

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  xModels: Model<Instance, unknown>[] = [];
  xDatasets: Dataset<Instance>[] = [];
  xPredictions: BatchPrediction[] = [];
  xDataStores: DataStore[] = [];
  xCurrentPID = -1;

  use(...components: Array<Component | Component[] | string>): ExperimentSettings {
    this.components = this.components.concat(components);
    return this;
  }

  dataStores(...stores: DataStore[]): ExperimentSettings {
    this.xDataStores = stores;
    return this;
  }

  models(...models: Model<Instance, unknown>[]): ExperimentSettings {
    this.xModels = models;
    return this;
  }

  datasets(...datasets: Dataset<Instance>[]): ExperimentSettings {
    this.xDatasets = datasets;
    return this;
  }

  pid(pid: number): ExperimentSettings {
    this.xCurrentPID = pid;
    return this;
  }

  mount(): void {
    for (const m of this.components) {
      if (isComponentArray(m)) {
        for (const n of m) {
          n.mount();
        }
      } else if (!isTitle(m)) {
        m.mount();
      }
    }
  }

  destroy(): void {
    for (const m of this.components) {
      if (isComponentArray(m)) {
        for (const n of m) {
          n.destroy();
        }
      } else if (!isTitle(m)) {
        m.destroy();
      }
    }
  }
}
