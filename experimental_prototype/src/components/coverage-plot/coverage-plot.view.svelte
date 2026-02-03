<script lang="ts">
  import { ViewContainer } from '@marcellejs/design-system';
  import { Stream } from '@marcellejs/core';
  import { ClassCoverage, Coverage } from './coverage-plot.component';
  import { Chart, ChartData, ChartOptions, registerables } from 'chart.js';
  import { onMount, createEventDispatcher} from 'svelte';

  const dispatch = createEventDispatcher();

  // Register Chart.js components
  Chart.register(...registerables);

  export let title: string;
  export let coverageStream: Stream<Coverage>;


  let chart : Chart;
  let chartContainer: HTMLCanvasElement;

  function createChart(classCoverage: ClassCoverage[]) {
    const ctx = chartContainer.getContext('2d'); 
    const labels = classCoverage.map(d => d.class);
    const passedData = classCoverage.map(d => d.passed);
    const failedData = classCoverage.map(d => d.failed);
    const uncheckedData = classCoverage.map(d => d.unchecked);

    const chartData: ChartData<'bar'> = {
      labels: labels,
      datasets: [
        {
          label: 'Unchecked',
          data: uncheckedData,
          backgroundColor: 'grey',
        },
        {
          label: 'Pass',
          data: passedData,
          backgroundColor: '#005AD3',
          //backgroundColor: '#4CA731',
        },
        {
          label: 'Fail',
          data: failedData,
          backgroundColor: '#FD0000',
        }
      ],
    };

    const options : ChartOptions<'bar'> = {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      scales: {
        x: {
          stacked: true,
        },
        y: {
          stacked: true
        }
      },
      animation: {
        duration: 0
      },
      
    }

    if (chart) {
      chart.destroy();
    }
    
    chart = new Chart(ctx, {
      type: 'bar',
      data: chartData,
      options: options,
    });
  }

  onMount(() => {
    const unsubscribe = coverageStream.subscribe((coverage) => {
      createChart(coverage.classCoverage);
    });
    return () => {
      if (chart) {
        chart.destroy();
      }
      unsubscribe();
      dispatch('chartCreated', { chart });
    };
    
  });

</script>

<ViewContainer {title}>
  Total number of test cases: {#if $coverageStream} {$coverageStream.totalNumberOfTestCases} {/if}
  <div class="plot-container">
    <canvas bind:this={chartContainer}></canvas>
  </div>
</ViewContainer>

<style>
  .plot-container {
    width: 100%; /* Ensure the parent container has a fixed width */
    height: 400px;
  }
</style>
