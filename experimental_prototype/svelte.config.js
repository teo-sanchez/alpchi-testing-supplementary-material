import sveltePreprocess from 'svelte-preprocess';

export default {
  // Consult https://github.com/sveltejs/svelte-preprocess
  // for more information about preprocessors
  preprocess: sveltePreprocess({
    postcss: true, // This tells svelte-preprocess to use your PostCSS configuration
}),
};
