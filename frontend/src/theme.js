// theme.js
import { extendTheme } from '@chakra-ui/react'

const theme = extendTheme({
    colors: {
        gold: '#FFD700',
        black: '#0B0B0C',
        gray: '#1A1A1D',
        goldLight: '#FFEB99',
        text: '#F8F8F8',
        thinking: '#C8B560',
        border: '#33331A',
    },

    styles: {
        global: {
            body: {
                bg: '#0B0B0C',
                color: '#F8F8F8',
            },
        },
    },
    components: {
        Button: {
            defaultProps: {
                colorScheme: 'synapsignalGold', // this has to be declared below
            },
        },
    },
})

export default theme