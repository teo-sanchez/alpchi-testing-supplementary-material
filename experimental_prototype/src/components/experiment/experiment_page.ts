import { Component } from '@marcellejs/core';
import {Stream} from '@marcellejs/core';
import {ExperimentPageOptions} from './index';
import { Experiment } from './index';
import { string2slug } from './utils';
import { never } from '@most/core';

function isTitle(x: Component | Component[] | string): x is string {
  return typeof x === 'string';
}

function isComponentArray(x: Component | Component[] | string): x is Component[] {
  return Array.isArray(x);
}

export class ExperimentPage {

  parentExperiment: Experiment;

  $ready: Stream<boolean> = new Stream(false, true); // TODO : implement

  $clickPrevious :Stream<string> = new Stream<string>(never());
  $clickNext :Stream<string> = new Stream<string>(never());

  $termination: Stream<boolean> = new Stream(false, true); //Stream triggering page change
  #terminationSubscription: any;
  nextPageSlugDefined: boolean = false;
  nextPageSlug: string = null;
  previousPageSlugDefined: boolean = false;
  previousPageSlug: string = null;

  $terminationDisplayStream: Stream<string> = new Stream('', true); //Stream set by the user to be displayed. Only subscribed to when the page is active to avoid interference with other pages.
  $terminationDisplay: Stream<string> = new Stream('', true); //Stream effectively displayed in the instruction bar
  #terminationDisplaySubscription: any;

  components: Array<Component | Component[] | string> = [];
  componentsLeft: Array<Component | Component[] | string> = [];
  componentsRight: Array<Component | Component[] | string> = [];

  $buttonDisabled : Stream<boolean> = new Stream(true, true);
  
  constructor(public options: ExperimentPageOptions, parentExperiment: Experiment) {

    this.parentExperiment = parentExperiment;

    // Set default options if not provided
    this.options.name = options.name || 'Page';
    this.options.instructions = options.instructions || 'Write instructions here';
    this.options.navigationMode = options.navigationMode || 'manual';
    this.options.navigationButtons = options.navigationButtons || (this.parentExperiment.freeNavigation ? "both" : (this.options.navigationMode === 'automatic' ? "none" : "next"));
    this.options.showInstructions = options.showInstructions || true;
    this.options.showTermination = options.showTermination && true;
    if (options.showLeftSidebar === undefined) {
      this.options.showLeftSidebar = true;
    }
    if (options.showRightSidebar === undefined) {
      this.options.showRightSidebar = true;
    }
    this.options.ratioLeftSidebar = options.ratioLeftSidebar || 0.2;
    this.options.ratioRightSidebar = options.ratioRightSidebar || 0.2;
    
    this.$buttonDisabled.set(!this.parentExperiment.freeNavigation);
    if (this.options.navigationMode === 'free'){
      this.$buttonDisabled.set(false);
    }

    this.setupSubscriptions();
 
  }

  private setupSubscriptions() {
    // Automatically set the next and previoius page slug
    this.parentExperiment.$panelsKeys.subscribe((keys) => {
      const currentPageIndex = keys.indexOf(this.options.name);

      if (currentPageIndex < keys.length - 1 && currentPageIndex >= 0 && !this.nextPageSlugDefined) {
          this.nextPageSlug = string2slug(keys[currentPageIndex + 1]);
          this.nextPageSlugDefined = true;
      }

      if (currentPageIndex > 0 && !this.previousPageSlugDefined) {
        this.previousPageSlug = string2slug(keys[currentPageIndex - 1]);
        this.previousPageSlugDefined = true;
      }
    });

    // Only subscribe to the termination stream if the user really is on this page. Otherwise, the terminations across pages will interfere.
    this.parentExperiment.$currentPageSlug
      .subscribe((x) => {
      if (x === string2slug(this.options.name) || (x === '' && string2slug(this.options.name) === string2slug(this.parentExperiment.$panelsKeys.get()[0]))) {
        // Subscription to termination stream in order to automatically change page
        if (!this.#terminationSubscription) {
          this.#terminationSubscription = this.$termination.subscribe((x) => {
            if (x && this.nextPageSlugDefined) {
              if (this.options.navigationMode === 'automatic') {
                this.parentExperiment.goToPage(this.nextPageSlug);
              } else {
                this.$buttonDisabled.set(false);
              }
            }
          });
        }
        // Subscription to termination display
        if (!this.#terminationDisplaySubscription) {
          this.#terminationDisplaySubscription = this.$terminationDisplayStream.subscribe((x) => {
            this.$terminationDisplay.set(x);
          });
        }
      }
    });
  }
  
  
  // // TODO : FIX : check if all components are ready. Must combine incrementally all ready streams into one.
  // private checkComponentReady(component: Component | Component[] | string): boolean {
  //   // Handle different component types
  //   if (typeof component === "string") {
  //     // ? : This is likely a spacer or non-interactive element
  //     return true;
  //   } else if (component instanceof Component) {
  //     // Has ready : boolean attribute;
  //     if('ready' in component && typeof component.ready === 'boolean') {
  //       console.log(component.title, 'ready', component.ready);
  //     }
  //     // Has ready : Stream<boolean> attribute;
  //     if('$ready' in component && component.$ready instanceof Stream) {
  //       component.$ready.subscribe((x) => {
  //         console.log(component.title, 'ready', x);
  //       });
  //     }
  //   } else if (Array.isArray(component)) {
  //     component.every(this.checkComponentReady);
  //   }
  // }

  use(...components: Array<Component | Component[] | string>): ExperimentPage {
    this.components = this.components.concat(components);
    return this;
  }

  useLeft(...components:  Array<Component | Component[] | string>): ExperimentPage {
    this.componentsLeft = this.componentsLeft.concat(components);
    return this;
  }

  useRight(...components: Array<Component | Component[] | string>): ExperimentPage {
    this.componentsRight = this.componentsRight.concat(components);
    return this;
  }

  setTerminationDisplay($userDisplayStream : Stream<string> ): ExperimentPage {
    this.$terminationDisplayStream = $userDisplayStream;
    this.$terminationDisplay.set($userDisplayStream.get());
    return this;
  }

  terminate($isTerminated : Stream<boolean>, targetPageSlug?: string): ExperimentPage {
    // Setup the page to switch to the next page when $isTerminated is true
    if (targetPageSlug) {
      this.nextPageSlug = targetPageSlug;
      this.nextPageSlugDefined = true;
    }
    // Setup the termination stream once the page is active (i.e. when the page is the current one, see constructor)
    this.$termination = $isTerminated;
    this.$termination.set($isTerminated.get());
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
    for (const m of this.componentsLeft) {
      if (isComponentArray(m)) {
        for (const n of m) {
          n.mount();
        }
      } else if (!isTitle(m)) {
        m.mount();
      }
    }
    for (const m of this.componentsRight) {
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
    for (const m of this.componentsLeft) {
      if (isComponentArray(m)) {
        for (const n of m) {
          n.destroy();
        }
      } else if (!isTitle(m)) {
        m.destroy();
      }
    }
    for (const m of this.componentsRight) {
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
