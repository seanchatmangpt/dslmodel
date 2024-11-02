// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  extends: ['@nuxt/ui-pro'],

  modules: [
    '@pinia/nuxt',
    '@nuxt/content',
    '@nuxt/eslint',
    '@nuxt/fonts',
    '@nuxt/image',
    '@nuxt/ui',
    '@nuxthq/studio',
    '@vueuse/nuxt',
    'nuxt-og-image',
    'pinia-plugin-persistedstate/nuxt'

  ],

  devtools: {
    enabled: true
  },

  colorMode: {
    disableTransition: true
  },

  runtimeConfig: {
    public: {
      FASTAPI_URL: process.env.FASTAPI_URL,
      SOCKET_URL: process.env.SOCKET_URL
    }
  },

  routeRules: {
    '/api/search.json': { prerender: true },
    '/docs': { redirect: '/docs/getting-started', prerender: false }
  },

  future: {
    compatibilityVersion: 4
  },

  compatibilityDate: '2024-07-11',

  nitro: {
    prerender: {
      routes: [
        '/',
        '/docs'
      ],
      crawlLinks: true
    },
    storage: {
      // Define Redis storage
      sharedData: {
        driver: 'redis',
        base: 'nuxt-shared',
        host: 'localhost',
        port: 6379
      }
    }
  },

  vite: {
    ssr: {
      noExternal: ['rxjs'] // Ensure Vite includes rxjs in the bundle instead of treating it as external
    }
  },

  typescript: {
    strict: false
  },

  hooks: {
    // Define `@nuxt/ui` components as global to use them in `.md` (feel free to add those you need)
    'components:extend': (components) => {
      const globals = components.filter(c => ['UButton'].includes(c.pascalName))

      globals.forEach(c => c.global = true)
    }
  },

  eslint: {
    config: {
      stylistic: {
        commaDangle: 'never',
        braceStyle: '1tbs'
      }
    }
  }
})
