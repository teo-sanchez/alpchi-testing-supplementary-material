import { Component, Stream } from '@marcellejs/core';
import View from './button-select.view.svelte';

export interface ButtonSelectOptions {
  variant?: 'outline' | 'filled' | 'light';
  type?: 'default' | 'success' | 'warning' | 'danger';
  size?: 'small' | 'medium' | 'large';
  round?: boolean;
}

export class ButtonSelect extends Component {
  title = 'Button selector';

  $options: Stream<ButtonSelectOptions>;

  $items: Stream<string[]>;

  $click : Stream<string>;
  $pressed: Stream<boolean[]> = new Stream([], true);
  
  $loading = new Stream(true, true);
  $disabled: Stream<boolean[]> = new Stream([], true);

  constructor(
    categories: string[] = ["Category 1", "Category 2", "Category 3"],
    options?: Partial<ButtonSelectOptions>) {

    super();
    options = {
      variant: 'light',
      type: 'default',
      size: 'large',
      round: false,
      ...options
    };
    // Initialize streams
    this.$options = new Stream(options, true);
    this.$items = new Stream(categories, true);

    this.$click = new Stream("", true);
    
    this.start();

    this.$items.subscribe(its => {
      const previousLength = this.$disabled.get().length;
      const currentLength = its.length;

      let disabled = this.$disabled.get();
      let pressedArr = this.$pressed.get();

      // Adjust lengths
      if (currentLength > previousLength) {
        disabled = [...disabled, ...Array(currentLength - previousLength).fill(false)];
        pressedArr = [...pressedArr, ...Array(currentLength - previousLength).fill(false)];
      } else if (currentLength < previousLength) {
        disabled = disabled.slice(0, currentLength);
        pressedArr = pressedArr.slice(0, currentLength);
      }

      // Update streams
      this.$disabled.set(disabled);
      this.$pressed.set(pressedArr);

      this.$loading.set(false);
    });
      
  }

  mount(target?: HTMLElement): void {
    const t = target || document.querySelector(`#${this.id}`);
    if (!t) return;
    this.destroy();
    this.$$.app = new View({
      target: t,
      props: {
        title: this.title,
        options: this.$options,
        items: this.$items,
        click: this.$click,
        pressed: this.$pressed,
        loading: this.$loading,
        disabled: this.$disabled,
      },
    });
  }
}