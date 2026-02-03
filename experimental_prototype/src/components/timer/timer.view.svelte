<svelte:options accessors />

<script lang="ts">
  import { ViewContainer } from '@marcellejs/design-system';
  import { Stream } from '@marcellejs/core';
  import { TimerTime } from './timer.component';

  export let title: string;
  export let time: Stream<TimerTime>;

  function getTimeString(el: number, countdown?: number) {
    // If a countdown is set, calculate the remaining time
    if (countdown) {
      el = countdown + 1000 - el;
    }

    // Create a new Date object with the elapsed time
    const date = new Date(null, null, null, null, null, null, el);

    // Convert to time string and split into [HH, MM, SS]
    const timeParts = date.toTimeString().split(' ')[0].split(':');

    // Return only the MM:SS part
    return timeParts[1] + ':' + timeParts[2];
  }

</script>

<ViewContainer {title}>
  <div class="flex-grow flex test">
      <p class={($time.countdown - $time.elapsed <= 20000) ? 'font-medium text-2xl red-text' : 'font-medium text-2xl'}>
          {getTimeString($time.elapsed, $time.countdown)}
      </p>
  </div>
</ViewContainer>

<style>
  .red-text {
  color: #F43F5E
  }
</style>
