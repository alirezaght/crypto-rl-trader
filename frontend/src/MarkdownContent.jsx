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

**Synap Signal** is an intelligent crypto assistant that analyzes the **most recent 90 days** of historical price and data to predict **the likely market movement over the next 14 days**. Our insights combine:

- Reinforcement Learning (RL)-based agent predictions  
- Technical indicators such as **RSI**, **MACD**, and **EMA**  
- Aggregated crypto news sentiment from trusted media sources  

> ⚠️ **Disclaimer**  
> This tool is intended **for informational and research purposes only**. It is not financial advice.  
> Always do your own research and consider multiple factors before making investment decisions.  

---

### 🔍 Additional Notes

- Predictions are **probabilistic** and should not be interpreted as guarantees.  
- Past performance of any model or signal is **not indicative of future results**.  
- The app does **not offer real-time data**. Market conditions may shift rapidly.  
- **No trades are executed automatically.** You are solely responsible for your own actions.  
- Trading cryptocurrencies carries **substantial risk** and may not be suitable for all investors.

---

💡 Use Synap Signal as an **additional source of insight**, alongside your own research and risk management strategy.

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