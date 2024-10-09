/**
 * plugins/vuetify.js
 *
 * Framework documentation: https://vuetifyjs.com`
 */

// Styles
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'

// Composables
import {createVuetify} from 'vuetify'

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
export default createVuetify({
  theme: {
    defaultTheme: "theme2",
    themes: {
      theme2: {
        dark: true,
        colors: {
          brighterBackground: '#282828',
          primary: '#17cb0e',
        }
      }
    }
  }
})
