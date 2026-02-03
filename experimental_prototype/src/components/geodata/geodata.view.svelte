<script lang="ts">
  import { ViewContainer } from '@marcellejs/design-system';
  import { Button } from '@marcellejs/design-system';
  import { createEventDispatcher, onMount, onDestroy, tick } from 'svelte';
  import Map from 'ol/Map.js';
  import TileLayer from 'ol/layer/Tile.js';
  import View from 'ol/View.js';
  import { XYZ } from 'ol/source';
  import { DblClickDragZoom, MouseWheelZoom, defaults as defaultInteractions } from 'ol/interaction.js';
  import { Coordinate } from 'ol/coordinate';
  import { fromPixelstoWGS } from './geodata.component';

  const dispatch = createEventDispatcher();

  // --------------------------------
  // Props from parent component
  // --------------------------------

  export let title: string;
  export let boundaries: Coordinate[];
  export let centerAtLoad: Coordinate;
  export let randomizeButton: boolean;
  export let centerButton: boolean;
  export let imageSize: number;


  let mapInstance: Map | null = null;
  let mapContainer: HTMLDivElement;

  let checkOverlayContainer: string | number | NodeJS.Timeout;
  let checkCanvas: string | number | NodeJS.Timeout;

  let alreadyInstanciated = false;

  // --------------------------------
  // Map configuration
  // --------------------------------
  
  function setRandomLocation() {
    // Random location using boundaries
    const randomX = Math.random() * (boundaries[1][0] - boundaries[0][0]) + boundaries[0][0];
    const randomY = Math.random() * (boundaries[0][1] - boundaries[1][1]) + boundaries[1][1];
    view.setCenter(fromPixelstoWGS([randomX, randomY]));
    dispatch('randomize', null);
  }

  function setBackToCenter() {
    view.setCenter(fromPixelstoWGS(centerAtLoad));
    dispatch('center', null);
  }

  const view = new View({
    center: fromPixelstoWGS(centerAtLoad),
    resolution: imageSize,
    enableRotation: true,
    maxZoom: 4,
    maxResolution: 5000,
    // minZoom: 5, // Minimum zoom level (the farthest zoom level)
    // maxZoom: 10, // Maximum zoom level (the closest zoom level)
    // extent: [topLeftCornerWGS[0], bottomRightCornerWGS[1], topLeftCornerWGS[1], bottomRightCornerWGS[0]],
    extent: [fromPixelstoWGS(boundaries[0])[0], 
             fromPixelstoWGS(boundaries[1])[1], 
             fromPixelstoWGS(boundaries[0])[1], 
             fromPixelstoWGS(boundaries[1])[0]],
  });


  // --------------------------------
  // Map initialization
  // --------------------------------

  onMount(async () => {
    await tick(); // Wait for the DOM to be updated
    const mapDiv = document.getElementById('map');
    if (alreadyInstanciated === false && (mapDiv && mapContainer)) {
      mapInstance = new Map({
        interactions: defaultInteractions().extend([
          new DblClickDragZoom(), 
          new MouseWheelZoom({
            constrainResolution: false, 
            timeout: 0,
            duration: 5,
          })]),
        layers: [
          new TileLayer({
            source: new XYZ({
              url: '/assets/tiles/{z}/{x}_{-y}.png',
              tileSize: 2500,
              maxZoom: 5,
              minZoom: 5
            }),
            preload: Infinity// Infinity, // Preload the tiles to reduce flickering when panning the map 
          }),
        ],
        target: mapDiv,
        view: view,
      });

      // Removing the overlay container
      checkOverlayContainer = setInterval(() => {
        const overlayContainer = mapDiv.querySelector('.ol-overlaycontainer-stopevent');
        if (overlayContainer) {
          overlayContainer.parentNode.removeChild(overlayContainer);
          clearInterval(checkOverlayContainer);
        }
      }, 100); // Check every 100 milliseconds until it can be removed


      // Dispatch the canvas for image stream
      const checkCanvas = setInterval(() => {
        const canvas = mapDiv.querySelector('canvas');
        // Check if the canvas is non-null, and mapInstance non-null, and view non-null
        if (alreadyInstanciated === false && canvas && mapInstance && view) {
          alreadyInstanciated = true;
          console.log("Canvas ready", alreadyInstanciated);
          dispatch('canvasReady', canvas);
          dispatch('mapReady', mapInstance);
          dispatch('viewReady', view);
          clearInterval(checkCanvas);
        }
      }, 100); // Check every 100 milliseconds
    }
  });

  onDestroy(() => {
    if (mapInstance) {
      mapInstance.setTarget(null);
      mapInstance = null;
    }
    if (checkOverlayContainer) {
      clearInterval(checkOverlayContainer);
    }
    if (checkCanvas) {
      clearInterval(checkCanvas);
    }
  });

</script>

<ViewContainer {title}>
  <div id='map' class='map' bind:this={mapContainer} style={'width: 390px; height: 390px;'}></div>
  <div class="m-1 flex justify-center items-center space-x-4">
    {#if randomizeButton}
      <Button type="default"  on:click={setRandomLocation}>Random Location</Button>
    {/if}
    {#if centerButton}
      <Button type="default"  on:click={setBackToCenter}>Back to city center</Button>
    {/if}
  </div>
</ViewContainer>


<style lang="postcss">
  @import "node_modules/ol/ol.css";
  .map {
    @apply justify-center items-center;
    margin: 0 auto;
  }
  .ol-overlaycontainer-stopevent {
    display: none !important;
  }
</style>
