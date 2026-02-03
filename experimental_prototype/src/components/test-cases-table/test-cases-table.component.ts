import { Component, Dataset, Instance, Stream } from '@marcellejs/core';
import View from './test-cases-table.view.svelte';
import type { Column } from '@marcellejs/design-system';

export type UserInteraction = {
  action: 'add' | 'select' | 'check' | 'delete' | 'sort' | string,
  numberOfItemsAffected?: number,
  object: string | string[] | Instance | Instance[]
  ascending?: boolean,
  timestamp: number,
}

export class TestCasesTable<T extends Instance> extends Component {
  title: string;
  columns: Column[];

  #dataset: Dataset<T>;
  $columnNames: Stream<string[]>;
  $selection: Stream<T[]> = new Stream([], true);
  $interactions: Stream<UserInteraction>;

  singleSelection : boolean = true;
  showTotalItems : boolean;

  constructor(dataset: Dataset<T>, columns: Column[], singleSelection: boolean = true, showTotalItems: boolean = false) {
    super();
    this.#dataset = dataset;
    this.singleSelection = singleSelection;
    this.showTotalItems = showTotalItems ? showTotalItems : false;
    this.columns = columns;
    this.$columnNames = new Stream(columns.map((c) => c.name));
    this.$interactions = new Stream({ action: 'init', object: '', timestamp: Date.now()} as UserInteraction);
    
    this.start();
  }

  mount(target?: HTMLElement): void {
    const t = target || document.querySelector(`#${this.id}`);
    if (!t) return;
    this.destroy();
    this.$$.app = new View({
      target: t,
      props: {
        title: this.title,
        dataset: this.#dataset,
        columns: this.columns,
        singleSelection: this.singleSelection,
        selection: this.$selection as any,
        interactions: this.$interactions,
        showTotalItems: this.showTotalItems,
      },
    });
  }
}
