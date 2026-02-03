import {Stream} from '@marcellejs/core';
import { ExperimentPage } from './experiment_page';
import ExperimentComponent from './Experiment.svelte';
import { ExperimentSettings } from './experiment_settings';
import { string2slug } from './utils';

export interface ExperimentOptions {
    title: string;
    author: string;
    fullscreen?: boolean;
    freeNavigation?: boolean;
    showHeader?: boolean;
    showFooter?: boolean;
    closable?: boolean;
}

export interface ExperimentPageOptions {
    name: string;
    instructions: string;
    navigationMode?: "free" | "manual" | "automatic";
    navigationButtons?: "none" | "next" | "previous" | "both";
    showInstructions?: boolean;
    showTermination?: boolean;
    showLeftSidebar?: boolean;
    ratioLeftSidebar?: number;
    showRightSidebar?: boolean;
    ratioRightSidebar?: number;
}


export interface ExperimentDesignParameters {
}


export class Experiment {
    $panels: Stream<Record<string, ExperimentPage>> = new Stream({}, true);
    $panelsKeys: Stream<string[]> = new Stream([], true);
    $slugifiedHash : Stream<string> = new Stream('', true);
    app? : ExperimentComponent;
    settings = new ExperimentSettings(); // TODO: implement 
    
    $ready: Stream<boolean> = new Stream(false, true);

    $active : Stream<boolean> = new Stream(false as boolean, true);
    $currentPageSlug : Stream<string> = new Stream('', true); 
    $currentPage : Stream<ExperimentPage> = new Stream(undefined, true);

    title: string;
    author: string;
    fullscreen: boolean;
    freeNavigation: boolean;
    showHeader: boolean;
    showFooter: boolean;
    closable: boolean;

    allowPageChange: boolean;

    constructor({
        title = "Research experiment template",
        author = "Author",
        fullscreen = true,
        freeNavigation = false,
        showHeader = true,
        showFooter = false,
        closable = false
    }: ExperimentOptions) {
        this.title = title;
        this.author = author || "Author";
        this.fullscreen = fullscreen || true;
        this.freeNavigation = freeNavigation || false;
        this.showHeader = showHeader || true;
        this.showFooter = showFooter || false;
        this.closable = closable || false;


        // Set the panels keys
        this.$panels.subscribe((x) => {
            this.$panelsKeys.set(Object.keys(x));
        });

        // Set the current page slug from the hash + handle hash change
        window.onhashchange = () => {
            this.setCurrentPageSlug();
            this.handleHashChange();
        }

        this.allowPageChange = this.freeNavigation;

        // Set current page from the current page slug
        this.$currentPageSlug.subscribe((slug) => {
            const pages = this.$panels.get();
            const key = slug === '' ? Object.keys(pages)[0] : Object.keys(pages).find(key => string2slug(key) === slug);
            if (key) {
                this.$currentPage.set(pages[key]);
            }
        });

    }

    private checkReady(): void {
        const pages = this.$panels.get();
        const ready = Object.values(pages).every(page => page.$ready.get());
        // for (const page of Object.values(pages)) {
        //     console.log(page.options.name, page.$ready.get())
        // }
        this.$ready.set(ready);
    }
    
    setFullscreen(bool : boolean): void {
        const doc = window.document as any;
        const docEl = doc.documentElement as any;

        const requestFullscreen = docEl.requestFullscreen || docEl.webkitRequestFullscreen || docEl.mozRequestFullScreen || docEl.msRequestFullscreen;

        const exitFullscreen = doc.exitFullscreen || doc.webkitExitFullscreen || doc.mozCancelFullScreen || doc.msExitFullscreen;

        const enterFullscreen = doc.fullscreenElement || doc.webkitFullscreenElement || doc.mozFullScreenElement || doc.msFullscreenElement;

        if (bool && !enterFullscreen) {
            if (requestFullscreen) {
                const promise = requestFullscreen.call(docEl);
                if (promise && promise.catch) {
                    promise.catch((err: Error) => {
                        console.error(`Error attempting to enable full-screen mode: ${err.message} (${err.name}). Browser may only allow full-screen mode in response to a user action.`);
                    });
                }
            }
        } else if (!bool && enterFullscreen) {
            if (exitFullscreen) {
                const promise = exitFullscreen.call(doc);
                if (promise && promise.catch) {
                    promise.catch((err: Error) => {
                        console.error(`Error attempting to disable full-screen mode: ${err.message} (${err.name}). Browser may only allow full-screen mode in response to a user action.`);
                    });
                }
            }
        }

    }


    goToPage(targetPageSlug: string): void {
        this.allowPageChange = true;
        const keys = this.$panelsKeys.get().map(key => string2slug(key));
        if (!keys.includes(targetPageSlug)) {
            throw new Error(`Page ${targetPageSlug} does not exist`);
        }
        else if (this.$currentPageSlug.get() !== targetPageSlug) {
            if (targetPageSlug === keys[0]) {
                targetPageSlug = '';
            }
            setTimeout(() => {
                window.location.hash = targetPageSlug; // Why does this does not trigger the router ?
            }, 300); // Feel smoother with a delay
        }
    }

    setCurrentPageSlug(): void {
        this.$slugifiedHash.set(window.location.hash.slice(1) || "");
        // Special case 1: settings
        if (this.$slugifiedHash.get() === 'settings') {
            this.$currentPageSlug.set("settings");
        }
         // Special case 2: first page
        else if (this.$slugifiedHash.get() === '') {
            this.$currentPageSlug.set(string2slug(this.$panelsKeys.get()[0]));
        }
        // Otherwise, check if the page slug is valid
        else if (this.isValidPageSlug(this.$slugifiedHash.get())) {
            this.$currentPageSlug.set(this.$slugifiedHash.get());
        }
    }

    isValidPageSlug(slug: string): boolean {
        const slugifiedPanelsNames = this.$panelsKeys.get().map(key => string2slug(key));
        return slug.length > 0 && slugifiedPanelsNames.includes(slug);
    }


    handleHashChange(): void {
        const isInSettings = this.$currentPageSlug.get() === 'settings';
        // Allow navigation from #settings to any other page no matter what (settings is for the experimenter, not participants)
        if (isInSettings) {
            return;
        }

        // Check if freeNavigation is false and the target page is not #settings (allow settings to be accessed at any time)
        if (!this.allowPageChange && this.$currentPageSlug.get() !== window.location.hash && window.location.hash !== '#settings') {
            window.location.hash = this.$currentPageSlug.get();
            alert("Please complete the current phase before navigating to next phase.");
        }

        // If the hash is not the same as the current page, update the current page
        if (this.allowPageChange != this.freeNavigation) {
            this.allowPageChange = this.freeNavigation;
        }
    }

    page( options : ExperimentPageOptions = {
        name: 'Page',
        instructions: "Write instructions here",
        navigationMode: "manual",
        navigationButtons: this.freeNavigation ? "both" : "next",
        showInstructions: true,
        showTermination: true,
        showLeftSidebar: true,
        ratioLeftSidebar: 0.2,
        showRightSidebar: true,
        ratioRightSidebar: 0.2
    }): ExperimentPage {
        const pages = this.$panels.get();
        if (pages[options.name]) { // Update the page options if it already exists
            const page = pages[options.name];
            page.options = options;
            page.$ready.subscribe(_ => this.checkReady());
            return page;
        } else { // Create a new page
            const page = new ExperimentPage(options, this);
            if (!this.freeNavigation && options.navigationMode === "automatic" && !options.navigationButtons) {
                page.options.navigationButtons = "none"; // Explicitly set to "none" for automatic navigation
            }
            this.$panels.set({
                ...pages,
                [options.name]: page
            });
            page.$ready.subscribe(_ => this.checkReady());
            return page;
        }
        
    }

    show(): void {
        this.app = new ExperimentComponent({
            target: document.body,
            props: {
                title: this.title,
                author: this.author,
                experimentPanels: this.$panels,
                settings: this.settings,
                currentPageSlug: this.$currentPageSlug,
                closable: this.closable,
                freeNavigation: this.freeNavigation,
                showHeader: this.showHeader,
                showFooter: this.showFooter,
            }
        });
        this.$active.set(true);
        this.app.$on('requestFullscreen', () => this.setFullscreen(this.fullscreen));
        this.app.$on('quit', () => {
            this.$active.set(false),
            this.app?.$destroy();
            for (const panel of Object.values(this.$panels.get())) {
                panel.destroy();
            }
            this.app = undefined;
        });
    }

    hide(): void {
        this.app?.quit();
    }
    
}

export function experiment(options: ExperimentOptions): Experiment {
    return new Experiment(options);
  }