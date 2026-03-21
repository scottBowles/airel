import { defineConfig, mergeConfig } from 'vitest/config';
import viteConfig from './vite.config';

export default mergeConfig(
	viteConfig,
	defineConfig({
		test: {
			include: ['src/**/*.{test,spec}.{js,ts}'],
			coverage: {
				provider: 'v8',
				reporter: ['text', 'html']
			}
		}
	})
);
