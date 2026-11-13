import { defineConfig } from 'astro/config';

// Adresy stron kończą się na .html (jak dotąd), więc format "preserve".
export default defineConfig({
  site: 'https://kantorblacksheep.pl',
  build: { format: 'preserve' },
  compressHTML: false,
});
