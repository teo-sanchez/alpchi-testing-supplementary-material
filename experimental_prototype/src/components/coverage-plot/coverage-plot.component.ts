import { Component, Dataset, isDataset, Instance } from '@marcellejs/core';
import View from './coverage-plot.view.svelte';
import { Stream } from '@marcellejs/core';
import { init } from 'svelte/internal';

export type ClassCoverage = {
  class: string,
  total: number,
  passed: number,
  failed: number,
  unchecked: number,
}

export type Coverage = { classCoverage : ClassCoverage[], totalNumberOfTestCases: number };


export class CoveragePlot<T extends Instance> extends Component {
  title: string = "Coverage plot";
  #dataset: Dataset<T>;
  #classes: string[];
  checkColumnName: string;
  labelColumnName: string;
  
  $coverageStream: Stream<Coverage> = new Stream<Coverage>({ classCoverage: [], totalNumberOfTestCases: 0 });

  private debounceTimeout: NodeJS.Timeout | null = null;

  constructor(dataset : Dataset<T>,
              classes : string[],
              labelColumnName: string, 
              checkColumnName: string) {
    super();
    this.#classes = classes;
    this.#dataset = dataset; 
    this.checkColumnName = checkColumnName;
    this.labelColumnName = labelColumnName;

    // Initialize all the coverage 
    
    this.#dataset.$changes.subscribe(async (_) => {
      this.debounceUpdateCoverage();
    });
    // this.updateCoverage();
    this.initCoverage(classes);
    this.start();
  }

  initCoverage(classes: string[]) {
    this.$coverageStream.set({ classCoverage: classes.map((c) => ({ class: c, total: 0, passed: 0, failed: 0, unchecked: 0 })), totalNumberOfTestCases: 0 });
  }

  debounceUpdateCoverage(delay: number = 50) {
    if (this.debounceTimeout) {
      clearTimeout(this.debounceTimeout);
    }
    this.debounceTimeout = setTimeout(async () => {
      await this.updateCoverage();
    }, delay);
  }

  async updateCoverage() {
    await this.#dataset.ready;
    if (!isDataset(this.#dataset)) return;

    // * Get classes
    const items = await this.#dataset.items().select([this.labelColumnName, this.checkColumnName]).toArray();

    const classCoverage: ClassCoverage[] = this.#classes.map((c) => {
      const filteredItems = items.filter((instance) => instance[this.labelColumnName] === c);
      const total = filteredItems.length;
      const passed = filteredItems.filter((instance) => instance[this.checkColumnName] === '🔵 Pass').length;
      const failed = filteredItems.filter((instance) => instance[this.checkColumnName] === '❌ Fail').length;
      const unchecked = filteredItems.filter((instance) => instance[this.checkColumnName] === '').length;

      return {
        class: c,
        total,
        passed,
        failed,
        unchecked,
      }
    });
    this.$coverageStream.set({ classCoverage, totalNumberOfTestCases: items.length });
  }


  mount(target?: HTMLElement): void {
    const t = target || document.querySelector(`#${this.id}`);
    if (!t) return;
    this.destroy();
    this.$$.app = new View({
      target: t,
      props: {
        title: this.title,
        coverageStream: this.$coverageStream,
      },
    });
    this.initCoverage(this.#classes);
    this.debounceUpdateCoverage();
    this.$$.app.$on('chartCreated', (elem) => {
      this.initCoverage(this.#classes);
      this.debounceUpdateCoverage();
    });
  }
}
