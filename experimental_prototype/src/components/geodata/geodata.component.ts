import { Component, Stream } from '@marcellejs/core';
import { never } from '@most/core';
import View from './geodata.view.svelte';
import {View as OLView} from 'ol';
import Map from 'ol/Map';
import { Coordinate } from 'ol/coordinate';
import { addProjection, addCoordinateTransforms} from 'ol/proj.js';
import Projection from 'ol/proj/Projection.js';

// ------------------------------
// Types
// ------------------------------

export interface GeodataOptions {
  captureMode?: 'any' | 'max_zoom';
  boundaries?: Coordinate[]; // x_min, y_min, x_max, y_max (Rectangle, in pixels)
  centerAtLoad? : Coordinate; // x, y (in pixels)
  randomizeButton?: boolean;
  centerButton?: boolean;
  imageSize?: number;
}

export type UserInteraction = {
  action: 'drag' | 'zoom' | 'randomize' | 'center' | 'init';
  coordinate: Coordinate;
  resolution: number;
  timestamp: number;
}

type CanvasProperties = { 
  readonly width: number;
  readonly height: number;
}

// ------------------------------
// Coordinate systems
// ------------------------------
// Default : EPSG:385 or Spherical Mercator projection or WGS
// Target custom projection : Pixels with (0,0) the top-left corner of the map

// Center of Munich (Mariensäule at Marienplatz)
// const munichCenterWGS = [-4253109.557903069, -4056732.4942354243];
// const munichCenterPixels = fromWGStoPixels(munichCenterWGS);  // 31509.703430159512, 28098.27744739379

// Define the default coordinates of the corners of the map
const topLeftCornerWGS = [-20037508.25412358, 10018754.024453176]
const bottomRightCornerWGS = [10018754.378508767, -20037508.061450925]

// Define the target coordinates of the corners of the map
const topLeftCornerPixels = [0, 0]
const bottomRightCornerPixels = [60000, 60000]

// Calculate scaling factors
const scaleX = (bottomRightCornerPixels[0] - topLeftCornerPixels[0]) / (bottomRightCornerWGS[0] - topLeftCornerWGS[0]);
const scaleY = (bottomRightCornerPixels[1] - topLeftCornerPixels[1]) / (bottomRightCornerWGS[1] - topLeftCornerWGS[1]);

// Define the custom projection
const customProjection = new Projection({
  code: 'Munich-Centric-Projection',
  units: 'pixels',
  extent: [topLeftCornerPixels[0], topLeftCornerPixels[1], bottomRightCornerPixels[0], bottomRightCornerPixels[1]],
});
// Add the custom projection to OpenLayers
addProjection(customProjection);

// Define transformation functions to convert between custom coordinates and pixel coordinates
export function fromWGStoPixels(coordinate : Coordinate): Coordinate {
  const x = (coordinate[0] - topLeftCornerWGS[0]) * scaleX + topLeftCornerPixels[0];
  const y = (coordinate[1] - topLeftCornerWGS[1]) * scaleY + topLeftCornerPixels[1];
  return [x, y];
};

export function fromPixelstoWGS(coordinate: Coordinate): Coordinate {
  const x = (coordinate[0] - topLeftCornerPixels[0]) / scaleX + topLeftCornerWGS[0];
  const y = (coordinate[1] - topLeftCornerPixels[1]) / scaleY + topLeftCornerWGS[1];
  return [x, y];
};

addCoordinateTransforms('EPSG:3857', customProjection, fromWGStoPixels, fromPixelstoWGS)

// ------------------------------
// Component logic / class
// ------------------------------

export class Geodata extends Component {
  title: string;
  captureMode: 'any' | 'max_zoom';
  boundaries: Coordinate[];
  centerAtLoad?: Coordinate; 
  randomizeButton: boolean; // Display a button to randomize the location on the map, within the GPS boundaries
  centerButton: boolean; // Display a button to center the map on the initial location
  imageSize: number;

  ready: boolean;

  view: OLView;
  map: Map;

  // Canvases and context
  canvasProps: CanvasProperties;
  #canvas: HTMLCanvasElement;
  #thumbnailWidth = 250;
  #thumbnailCanvas: HTMLCanvasElement;
  #thumbnailCanvasContext: CanvasRenderingContext2D;

  $images = new Stream<ImageData>(never(), true);
  $thumbnails = new Stream<string>(never(), true);
  $currentCoordinate = new Stream<Coordinate>(never(), true);
  $interactions = new Stream<UserInteraction>(never(), true);
  $zoomLevel = new Stream<number>(never(), true);
  $resolutionLevel = new Stream<number>(never(), true);
  $reachedMaxResolution = new Stream<boolean>(never(), true);

  // ------------------------------
  // Class constructor
  // ------------------------------

  constructor({captureMode = 'max_zoom',
                boundaries = [[0,0], [60000, 60000]],
                centerAtLoad = [31509.703430159512, 28098.27744739379], // Center of Munich, Mariensaüle statue at Marienplatz
                randomizeButton = true,
                centerButton = true,
                imageSize = 250} : GeodataOptions = {}) {
    super();
    // Initialize options with default values
    this.title = 'Geodata';
    this.captureMode = captureMode === undefined ? 'max_zoom' : captureMode;
    this.boundaries = boundaries === undefined ?  [[0, 0] , [60000, 60000]]: boundaries;
    this.centerAtLoad = centerAtLoad === undefined ? [31509.703430159512, 28098.27744739379] : centerAtLoad;
    this.randomizeButton = randomizeButton === undefined ? true : randomizeButton;
    this.centerButton = centerButton === undefined ? true : centerButton;
    this.imageSize = imageSize === undefined ? 250 : imageSize;

    this.ready = false;

    this.canvasProps = {
      width: imageSize,
      height: imageSize
    }

    // Setup the component
    this.setup();
    
    // Capture every 200ms after waiting 1 second to be sure 

    this.$reachedMaxResolution.subscribe((value : boolean) => {
      const canvasContainer = this.#canvas?.parentElement?.parentElement?.parentElement;
      if (canvasContainer) {
        // Remove existing border classes
        canvasContainer.classList.remove('border-4', 'border-cyan-500', 'border-white');
    
        // Add the new border class based on the condition
        if (value && this.captureMode === 'max_zoom') {
          canvasContainer.classList.add('border-4', 'border-cyan-500', 'border-dashed');
        } else if (!value && this.captureMode === 'max_zoom') {
          // Add a red border to the canvas
          canvasContainer.classList.add('border-4', 'border-white');
        }
      }
    });

    this.start();
  };

  // ------------------------------
  // Initialization methods
  // ------------------------------

  setup() : void {
    // Setup canvas width ? 
    // Setup thumbnail canvas ?
    this.#thumbnailCanvas = document.createElement('canvas');
    this.#thumbnailCanvas.width = this.#thumbnailWidth;
    this.#thumbnailCanvas.height = this.#thumbnailWidth;
    this.#thumbnailCanvasContext = this.#thumbnailCanvas.getContext('2d');
  }

    // ------------------------------
    // Capture methods
    // ------------------------------

  private capture() : void {
    this.$images.set(this.captureImage());
    this.$thumbnails.set(this.captureThumbnail());
  }

  private captureImage(): ImageData {
    const originalWidth = this.#canvas.width;
    const originalHeight = this.#canvas.height;
  
    // Create an off-screen canvas to resize the image
    const offScreenCanvas = document.createElement('canvas');
    offScreenCanvas.width = this.imageSize;
    offScreenCanvas.height = this.imageSize;
    const offScreenContext = offScreenCanvas.getContext('2d');

    // Calculate the scaling factors to maintain aspect ratio
    const scaleX = this.imageSize / originalWidth;
    const scaleY = this.imageSize / originalHeight;
    const scale = Math.min(scaleX, scaleY);
  
    // Calculate the new dimensions while maintaining aspect ratio
    const drawWidth = originalWidth * scale;
    const drawHeight = originalHeight * scale;
    
    // Clear the canvas and draw the resized image, centered on the off-screen canvas
    offScreenContext.clearRect(0, 0, this.imageSize, this.imageSize);
    
    // This will center the image in the off-screen canvas
    const dx = (this.imageSize - drawWidth) / 2;
    const dy = (this.imageSize - drawHeight) / 2;
  
    // Use drawImage to properly scale the image
    offScreenContext.drawImage(
      this.#canvas,
      0, 0, originalWidth, originalHeight, // Source rectangle
      dx, dy, drawWidth, drawHeight // Destination rectangle
    );
  
    // Get the resized image data from the off-screen canvas
    return offScreenContext.getImageData(0, 0, this.imageSize, this.imageSize);
  }

  downloadLastImage() {
    // Get the last image from $images stream
    const lastImage = this.$images.get();
    if (!lastImage) {
      console.error("No image available to download");
      return;
    }

    // Create an off-screen canvas to draw the ImageData
    const canvas = document.createElement('canvas');
    canvas.width = lastImage.width;
    canvas.height = lastImage.height;
    const ctx = canvas.getContext('2d');
    ctx.putImageData(lastImage, 0, 0);

    // Convert the canvas to a base64 string
    const dataURL = canvas.toDataURL('image/png');

    // Create a temporary link element to trigger the download
    const link = document.createElement('a');
    link.href = dataURL;
    link.download = 'captured_image.png';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  private imageDataToBase64(imageData: ImageData, format: string = 'image/jpeg'): string {
    // Create an off-screen canvas
    const canvas = document.createElement('canvas');
    canvas.width = imageData.width;
    canvas.height = imageData.height;
  
    // Draw the ImageData onto the canvas
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.putImageData(imageData, 0, 0);
    }
  
    // Convert the canvas to a data URL (base64 string)
    return canvas.toDataURL(format);
  }

  private captureThumbnail() : string {
    this.#thumbnailCanvasContext.drawImage(this.#canvas, 0, 0, this.#thumbnailWidth, this.#thumbnailWidth);
    return this.imageDataToBase64(this.#thumbnailCanvasContext.getImageData(0, 0, this.#thumbnailWidth, this.#thumbnailWidth));
  }



  handleUserInteraction(action: "drag" | "zoom" | "randomize" | "center" | "init", event: any) {
    // Get current state of the map
    const zoomLevel = this.view.getZoom();
    const resolutionLevel = this.view.getResolution();
    const coordinate = fromWGStoPixels(this.view.getCenter());
    const timestamp = Date.now();

    // Update streams
    this.$zoomLevel.set(zoomLevel);
    this.$resolutionLevel.set(resolutionLevel);
    this.$currentCoordinate.set(coordinate);
    this.$interactions.set({ action: action, coordinate : coordinate, resolution : resolutionLevel, timestamp: timestamp});

    // Max resolution level reached ?
    const epsilon = 10;
    const oldReachedMaxResolutionValue = this.$reachedMaxResolution.get();
    const newReachedMaxResolutionValue = Math.abs(resolutionLevel - this.view.getMinResolution()) < epsilon;
    if (oldReachedMaxResolutionValue !== newReachedMaxResolutionValue) {
      this.$reachedMaxResolution.set(newReachedMaxResolutionValue);
    }

    // Capture the image
    if (this.captureMode === 'any') {
      this.capture();
    } else if (this.captureMode === 'max_zoom' && newReachedMaxResolutionValue) {
      this.capture();
    }
  };

  mount(target?: HTMLElement): void {
    const t = target || document.querySelector(`#${this.id}`);
    if (!t) return;
    this.destroy();
    this.$$.app = new View({
      target: t,
      props: {
        title: this.title,
        boundaries: this.boundaries,
        centerAtLoad: this.centerAtLoad,
        randomizeButton: this.randomizeButton,
        centerButton: this.centerButton,
        imageSize: this.canvasProps.width
      },
    });
    this.$$.app.$on('canvasReady', (elem) => {
      this.#canvas = elem.detail;
      if (this.captureMode === 'max_zoom') {
        this.#canvas.parentElement.parentElement.parentElement.classList.add('border-4', 'border-cyan-500', 'border-dashed');
      }
    });
    this.$$.app.$on('mapReady', (elem) => {
      this.map = elem.detail;
    });
    this.$$.app.$on('viewReady', (elem) => {
      this.view = elem.detail;
      this.ready = true;
      this.handleUserInteraction('init', null);
      setInterval(() => this.capture(), 200)
      // Listen to view changes (drag, zoom, and randomize)
      this.map.on(['pointerdrag'],
         this.handleUserInteraction.bind(this, 'drag'));
      // Zoom out or in
      this.view.on(['change:resolution'], 
        this.handleUserInteraction.bind(this, 'zoom'));
      }); 
    this.$$.app.$on('randomize', () => {
      this.handleUserInteraction('randomize', null);
    });
    this.$$.app.$on('center', () => {
      this.handleUserInteraction('center', null);
    });
  }
}