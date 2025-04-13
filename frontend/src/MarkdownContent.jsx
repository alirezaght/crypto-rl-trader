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
## Welcome to Synap Signal

This app analyzes the **past 90 days** of historical price data for a selected cryptocurrency pair, combines it with insights from our custom-built **Reinforcement Learning (RL) agent**, and incorporates the **latest news headlines** from trusted crypto media sources.

Our goal is to generate an intelligent signal suggesting whether to:

- **Buy**
- **Sell**
- **Hold**

based on a synthesis of data, market conditions, and AI-generated reasoning.

> ⚠️ **Disclaimer**  
> This is _not_ financial advice. Use this tool as **an additional source of insight**, not a definitive guide. Always do your own research, consider multiple factors before trading, and make informed decisions.  
> We do not take any responsibility for financial actions based on the content provided.
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