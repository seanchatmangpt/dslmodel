// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  extends: ['@nuxt/ui-pro'],

  modules: [
    '@nuxt/content',
    '@nuxt/eslint',
    '@nuxt/fonts',
    '@nuxt/image',
    '@nuxt/ui',
    '@nuxthq/studio',
    '@vueuse/nuxt',
    'nuxt-og-image'
  ],

  hooks: {
    // Define `@nuxt/ui` components as global to use them in `.md` (feel free to add those you need)
    'components:extend': (components) => {
      const globals = components.filter(c => ['UButton'].includes(c.pascalName))

      globals.forEach(c => c.global = true)
    }
  },

  colorMode: {
    disableTransition: true
  },

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

  routeRules: {
    '/api/search.json': {prerender: true},
    '/docs': {redirect: '/docs/getting-started', prerender: false}
  },

  devtools: {
    enabled: true
  },

  typescript: {
    strict: false
  },

  future: {
    compatibilityVersion: 4
  },

  eslint: {
    config: {
      stylistic: {
        commaDangle: 'never',
        braceStyle: '1tbs'
      }
    }
  },

  runtimeConfig: {
    public: {
      FASTAPI_URL: process.env.FASTAPI_URL,
      SOCKET_URL: process.env.SOCKET_URL
    }
  },

  compatibilityDate: '2024-07-11'
})
