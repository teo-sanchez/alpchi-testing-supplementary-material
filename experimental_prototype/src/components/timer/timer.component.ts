import { Component, Stream } from '@marcellejs/core';
import View from './timer.view.svelte';

export interface TimerOptions {
  accuracy: number;
}

export interface TimerTime {
  start: DOMHighResTimeStamp,
  last: DOMHighResTimeStamp,
  stop: null | DOMHighResTimeStamp,
  elapsed: number,
  countdown: null | number,
  state: 'started' | 'stopped' | 'paused' | 'running'
}

/**
 * Accurate timer;
 * see: https://stackoverflow.com/a/29972322
 */
export class Timer extends Component {
  title: string = 'Timer';
  options: TimerOptions;

  private interval: number; // milliseconds;
  private timeout: any; // actually number, or NodeJS.Timeout, according to env...

  $time: Stream<TimerTime>;
  $formattedTime: Stream<string>;
  $finished : Stream<boolean> = new Stream(false);
  

  constructor(options: TimerOptions = {
    accuracy: 0,
  }) {
    super();
    this.options = options;
    this.$time = new Stream({
      start: null,
      last: null,
      state: 'stopped',
      stop: null,
      countdown: null,
      elapsed: 0,
    } as TimerTime, true);

    this.$formattedTime = new Stream('00:00'); // Initialize with '00:00'
    this.$finished = this.$time.map((time) => time.state === 'stopped');
  }


  /** 
   * Starts the timer.
   * 
   * @param countdown if present, then stopped after countdown milliseconds.
   * @param interval timestep for checking, in milliseconds.
   */

  public startTimer(opt: {
    countdown?: number,
    interval?: number
  }) {
    if (!opt.interval) {
      opt.interval = 1000 / (2 * (this.options.accuracy + 1));
    }
    this.interval = opt.interval;
    const begin = performance.now(); //new Date();
    this.$time.set({
      ...this.$time.value,
      start: begin,
      state: 'started',
      stop: null,
      countdown: opt.countdown
    });
    this.launch(this.interval - this.interval);
  }

  /** 
   * Pauses or resumes the timer based on the provided parameter.
   * 
   * @param shouldPause if true, pause, else resume
   * @returns 
   */
  public pauseTimer(shouldPause: boolean) {
    const isPaused = this.$time.value.state === 'paused';
    this.$time.set({
      ...this.$time.value,
      state: shouldPause ? 'paused' : 'started'
    })
    if (shouldPause && !isPaused) {
      this.clear();
    }
    else if (!shouldPause && isPaused) {
      this.launch(this.interval);
    }
  }

  /**
   * Stops the timer.
   */
  public stopTimer(): void {
    const isStopped : boolean = this.$time.value.state === 'stopped';
    if (isStopped) {
      return;
    }
    this.$time.set({
      ...this.$time.value,
      stop: performance.now(), //new Date(),
      state: 'stopped'
    });
    this.clear();
    }



  private launch(expected: number) {
    const step = () => {
      // from: https://stackoverflow.com/a/29972322
    const time = this.$time.value;
    const current = performance.now();//new Date();
    const drift = (current - time.last) - expected;
    if (Math.abs(drift) > this.interval) {
      console.warn('big lag');
    }
    this.$time.set({
      ...time,
      last: current,
      elapsed: time.elapsed + expected + drift,
      state: 'running',
    });
    if (time.countdown && time.elapsed > time.countdown) {
      this.stopTimer();
    }
    else {
      this.updateFormattedTime(time.elapsed, time.countdown);
      this.timeout = setTimeout(step, Math.max(0, this.interval - drift));
    }
  };
  this.$time.set({
    ...this.$time.value,
    last: performance.now(), //new Date(),
  });
  this.timeout = setTimeout(step, this.interval);
  }

  private updateFormattedTime(elapsed: number, countdown?: number) {
    const remaining = countdown ? countdown - elapsed : elapsed;
    const minutes = Math.floor(remaining / 60000);
    const seconds = Math.floor((remaining % 60000) / 1000);
    const formatted = `${minutes.toString().padStart(2, '0')}:${(seconds+1).toString().padStart(2, '0')}`;
    this.$formattedTime.set(formatted);
  }

  private clear() {
    if (this.timeout) {
      clearTimeout(this.timeout);
      this.timeout = null;
    }
  }

  mount(target?: HTMLElement): void {
    const t = target || document.querySelector(`#${this.id}`);
    if (!t) return;
    this.destroy();
    this.start();
    this.$$.app = new View({
      target: t,
      props: {
        title: this.title,
        time: this.$time,
      },
    });
  }
}
