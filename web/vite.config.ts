import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite';
import houdini from 'houdini/vite';

export default defineConfig({ 
	plugins: [houdini(), tailwindcss(), sveltekit()] 
});
