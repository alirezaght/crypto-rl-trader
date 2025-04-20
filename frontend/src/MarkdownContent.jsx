import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import {
  Box,
  Text,
  Heading,
  UnorderedList,
  ListItem,
  Code,
  Button,
} from '@chakra-ui/react'

const markdown = `
## 📘 Trading Terms & Disclaimers

**Synap Signal** is an intelligent market assistant that analyzes historical price, volume, and technical data to provide insights into potential future movements in both **crypto** and **stock markets**. Our predictions are powered by:

- Reinforcement Learning (RL)-based agent models  
- A diverse set of technical indicators such as **RSI**, **MACD**, **EMA**, **Stochastic Oscillator**, **Bollinger Bands**, **ADX**, and others
- Aggregated news sentiment from trusted financial and crypto sources  

> ⚠️ **Disclaimer**  
> This tool is intended **for informational and research purposes only**. It does not constitute financial advice.  
> Always perform your own due diligence and consider multiple perspectives before making investment decisions.  

---

### 🔍 Additional Notes

- Predictions are **probabilistic**, not guarantees.  
- Past performance of any model or signal is **not indicative of future results**.  
- The app does **not offer real-time data**. Market conditions may change quickly.  
- **No trades are executed automatically.** You are fully responsible for any trading decisions made based on this tool.  
- Trading cryptocurrencies and stocks involves **significant risk**, and may not be suitable for all investors.

---

💡 Use Synap Signal as a **complementary insight tool**, alongside your own research, experience, and financial strategy.

---

**Like this app? Support Synap Signal with a donation:**  

[Donate via Stripe](https://buy.stripe.com/14k16zbdK7jc7ba000)
`

const MarkdownContent = () => (
    <Box mb={6}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
            h1: (props) => <Heading as="h1" size="xl" my={4} textAlign="center" {...props} />,
            h2: (props) => <Heading as="h2" size="lg" my={4} textAlign="center" {...props} />,
            h3: (props) => <Heading as="h3" size="md" my={4} {...props} />,
            p: (props) => <Text my={2} {...props} />,
            ul: (props) => <UnorderedList pl={6} my={2} {...props} />,
            li: (props) => <ListItem my={1} {...props} />,
            blockquote: ({ children }) => (
                <Box
                  borderLeft="4px solid"
                  borderColor="gray.400"
                  pl={4}
                  color="gray.600"
                  my={4}
                  fontStyle="italic"
                >
                  {children}
                </Box>
              ),
            strong: (props) => <Text as="strong" fontWeight="bold" {...props} />,
            code: (props) => <Code colorScheme="yellow" p={1} {...props} />,
            a: ({ href, children }) =>
              href === 'https://buy.stripe.com/14k16zbdK7jc7ba000' ? (
                <Button
                  as="a"
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  colorScheme="gold"
                  bg="black"
                  color="gold"
                  size="sm"
                  mt={4}
                >
                  💛 {children}
                </Button>
              ) : (
                <Text as="a" color="blue.400" href={href} target="_blank" rel="noopener noreferrer">
                  {children}
                </Text>
              ),
          }}
      >
        {markdown}
      </ReactMarkdown>
    </Box>
  )

export default MarkdownContent