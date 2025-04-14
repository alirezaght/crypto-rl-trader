// src/App.jsx
import React, { useEffect, useState } from 'react'
import {
  Box,
  Heading,
  Text,
  VStack,
  Button,
  Input,
  useToast,
  Drawer,
  DrawerBody,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  IconButton,
  Flex,
  Spinner,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
} from '@chakra-ui/react'
import { FaGoogle } from 'react-icons/fa'
import logo from './assets/logo.png'
import { Image } from '@chakra-ui/react'
import { HamburgerIcon, ChevronDownIcon } from '@chakra-ui/icons'
import ReactMarkdown from 'react-markdown'
import { initializeApp } from 'firebase/app'
import {
  getAuth,
  onAuthStateChanged,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  signInWithPopup,
  GoogleAuthProvider,
} from 'firebase/auth'
import MarkdownContent from './MarkdownContent'
import { Global } from '@emotion/react'

const firebaseConfig = {
  apiKey: "AIzaSyBr3tD3w8_35ouHIXbtC0mHbzFl-LZqCZ0",
  authDomain: "silver-treat-456607-e6.firebaseapp.com",
  projectId: "silver-treat-456607-e6",
  storageBucket: "silver-treat-456607-e6.firebasestorage.app",
  messagingSenderId: "327272059000",
  appId: "1:327272059000:web:68fc9edea7ff1877ff1d8d",
  measurementId: "G-ZY38R9FRE4"
}

const appUrl = "https://app.synapsignal.com"
// const appUrl = "http://localhost:8000"

const app = initializeApp(firebaseConfig)
const auth = getAuth(app)
const googleProvider = new GoogleAuthProvider()

export default function App() {
  const [user, setUser] = useState(null)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLogin, setIsLogin] = useState(true)
  const [loading, setLoading] = useState(false)
  const [config, setConfig] = useState(null)
  const [selectedPair, setSelectedPair] = useState('')
  const [llmText, setLlmText] = useState('')
  const [thinkingText, setThinking] = useState('')
  const [streaming, setStreaming] = useState(false)
  const [llmPage, setLLMPage] = useState(false)
  const toast = useToast()
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)
  const [configLoading, setConfigLoading] = useState(true)

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      setUser(user)
      setSelectedPair('')
      setLlmText('')
      setThinking('')
      setLLMPage(false)
      if (user) {
        try {
          const token = await user.getIdToken()
          const res = await fetch(`${appUrl}/config`, {
            headers: { Authorization: `Bearer ${token}` }
          })
          const data = await res.json()
          setConfig(data)
        } catch (e) {
          toast({ title: "Error loading config", description: e.message, status: "error" })
        } finally {
          setConfigLoading(false)
        }
      } else {
        setConfigLoading(false)
      }
    })
    return () => unsubscribe()
  }, [toast])

  const handleAuth = async () => {
    try {
      setLoading(true)
      isLogin
        ? await signInWithEmailAndPassword(auth, email, password)
        : await createUserWithEmailAndPassword(auth, email, password)
    } catch (err) {
      toast({ title: "Auth Error", description: err.message, status: "error" })
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleLogin = async () => {
    try {
      setLoading(true)
      await signInWithPopup(auth, googleProvider)
    } catch (err) {
      toast({ title: "Google Auth Error", description: err.message, status: "error" })
    } finally {
      setLoading(false)
    }
  }

  const fetchLLMStreamSummary = async () => {
    if (!user) return
    setLlmText('')
    setStreaming(true)
    setLLMPage(true)

    try {
      const token = await user.getIdToken()
      const res = await fetch(`${appUrl}/llm-summary`, {
        headers: { Authorization: `Bearer ${token}` }
      })

      if (!res.ok) throw new Error("Failed to stream LLM response.")

      const reader = res.body.getReader()
      const decoder = new TextDecoder("utf-8")

      let done = false
      while (!done) {
        const { value, done: doneReading } = await reader.read()
        done = doneReading
        const chunk = decoder.decode(value || new Uint8Array(), { stream: !done })
        if (chunk) {
          setStreaming(false)
          if (chunk.startsWith("<thinking>") && chunk.endsWith("</thinking>")) {
            const thinkingText = chunk.slice(10, -11)
            setThinking(thinkingText)
          } else {
            setThinking('')
            setLlmText(prev => prev + chunk)
          }
        }
      }
    } catch (err) {
      toast({ title: "LLM Error", description: err.message, status: "error" })
    }

  }

  const fetchLLMStream = async (symbol) => {
    if (!user) return
    setLlmText('')
    setStreaming(true)
    setLLMPage(true)

    try {
      const token = await user.getIdToken()
      const res = await fetch(`${appUrl}/llm-stream?symbol=${encodeURIComponent(symbol)}`, {
        headers: { Authorization: `Bearer ${token}` }
      })

      if (!res.ok) throw new Error("Failed to stream LLM response.")

      const reader = res.body.getReader()
      const decoder = new TextDecoder("utf-8")

      let done = false
      while (!done) {
        const { value, done: doneReading } = await reader.read()
        done = doneReading
        const chunk = decoder.decode(value || new Uint8Array(), { stream: !done })
        if (chunk) {
          setStreaming(false)
          if (chunk.startsWith("<thinking>") && chunk.endsWith("</thinking>")) {
            const thinkingText = chunk.slice(10, -11)
            setThinking(thinkingText)
          } else {
            setThinking('')
            setLlmText(prev => prev + chunk)
          }
        }
      }
    } catch (err) {
      toast({ title: "LLM Error", description: err.message, status: "error" })
    }
  }

  const renderAuthForm = () => (
    <Flex minH="80vh" align="center" justify="center">
      <Box
        bg="black"
        p={8}
        rounded="md"
        boxShadow="lg"
        width="100%"
        maxW="sm"
      >
        <VStack spacing={4} align="stretch">
          <Heading textAlign="center" size="md" color="gray.700">
            {isLogin ? "Login to Synap Signal" : "Create your account"}
          </Heading>
          <Input
            bg="black"
            _hover={{ borderColor: "gold" }}
            _focus={{ borderColor: "gold" }}
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            variant="filled"
          />
          <Input
            bg="black"
            _hover={{ borderColor: "gold" }}
            _focus={{ borderColor: "gold" }}
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            variant="filled"
          />
          <Button colorScheme="gold" onClick={handleAuth} isLoading={loading}
            variant="outline">
            {isLogin ? "Login" : "Sign Up"}
          </Button>
          <IconButton
            aria-label="Login with Google"
            icon={<FaGoogle />}
            onClick={handleGoogleLogin}
            colorScheme="gold"
            variant="solid"
            isLoading={loading}
            alignSelf="center"
            size="lg"
          />
          <Button
            variant="link"
            color="gold"
            onClick={() => setIsLogin(!isLogin)}
            textAlign="center"
          >
            {isLogin ? "Create an account" : "Back to Login"}
          </Button>
        </VStack>
      </Box>
    </Flex>
  )

  return (

    <Box>
      <Flex justify="space-between" p={4} bg="gray" align="center">
        <IconButton color={"gold"} icon={<HamburgerIcon />} onClick={() => setIsDrawerOpen(true)} />
        <Image
          src={logo}
          alt="SynapSignal Logo"
          boxSize="72px"
          cursor="pointer"
          onClick={() => {
            setSelectedPair('')
            setLlmText('')
            setThinking('')
          }}
        />
        {user && (
          <Button color={"gold"} variant="outline" onClick={() => signOut(auth)}>Sign out</Button>
        )}
      </Flex>

      <Drawer isOpen={isDrawerOpen} placement="left" onClose={() => setIsDrawerOpen(false)}>
        <DrawerOverlay />
        <DrawerContent bg="black" color="text">
          <DrawerCloseButton color={"gold"} />
          <DrawerHeader color={"gold"}>Account</DrawerHeader>
          <DrawerBody>
            {user ? (
              <Text fontSize="sm">Logged in as <strong>{user.email}</strong></Text>
            ) : (
              <Text>Not signed in</Text>
            )}
            <Button
              mt={4}
              colorScheme="gold"
              bg="gold"
              color="black"
              onClick={() => window.open('https://buy.stripe.com/14k16zbdK7jc7ba000', '_blank')}
            >
              💛 Donate
            </Button>
          </DrawerBody>
        </DrawerContent>
      </Drawer>

      <Box p={4} maxW="4xl" mx="auto">
        {!user ? renderAuthForm() :
          (
            configLoading ? (
              <Flex justify="center" align="center" minH="50vh">
                <Spinner color="gold" size="xl" thickness="4px" />
              </Flex>
            ) :
              (
                <>
                  {!llmPage && (
                    <>
                      <MarkdownContent />
                    </>
                  )}
                  <Flex justify="left" align={"center"} >
                    <Menu>
                      <MenuButton as={Button}
                        minW="200px"
                        rightIcon={<ChevronDownIcon />} mb={4} colorScheme="gold" color="black" bg="gold">
                        {selectedPair || "Select a crypto pair"}
                      </MenuButton>
                      <MenuList bg="black" color="text" borderColor="border">
                        {config?.pairs.map(pair => (
                          <MenuItem
                            key={pair}
                            bg="black"
                            _hover={{ bg: 'gray', color: 'gold' }}
                            onClick={() => {
                              setSelectedPair(pair)
                              fetchLLMStream(pair)
                            }}
                          >
                            {pair}
                          </MenuItem>
                        ))}
                      </MenuList>
                    </Menu>
                  </Flex>

                  {!llmPage && (
                    <>
                      <Button
                        mt={4}
                        colorScheme="gold"
                        color={"black"}
                        bg="gold"
                        onClick={() => {
                          fetchLLMStreamSummary()
                        }}
                      >
                        Summarize
                      </Button>
                      <Box mt={4} mb={6} p={4} bg="gray" rounded="md">
                        <Heading as="h3" size="sm" mb={2} color="gold">
                          Can't find your favorite pair?
                        </Heading>
                        <Text fontSize="sm" mb={2}>Suggest a new pair you'd like to see supported:</Text>
                        <form
                          onSubmit={async (e) => {
                            e.preventDefault()
                            const formData = new FormData(e.target)
                            const suggestion = formData.get("pair")
                            if (suggestion) {
                              const token = await user.getIdToken()
                              fetch(`${appUrl}/suggest-pair`, {
                                method: "POST",
                                headers: {
                                  "Content-Type": "application/json",
                                  "Authorization": `Bearer ${token}`
                                },
                                body: JSON.stringify({ pair: suggestion })
                              }).then(res => {
                                if (!res.ok) {
                                  toast({
                                    title: "Error!",
                                    description: `Failed to submit your request.`,
                                    status: "error",
                                    duration: 4000,
                                    isClosable: true,
                                  })
                                  return;
                                }
                                toast({
                                  title: "Thank you!",
                                  description: `We've received your request: ${suggestion}`,
                                  status: "success",
                                  duration: 4000,
                                  isClosable: true,
                                })
                              })

                              e.target.reset()
                              // Optionally: Send to backend or email service here
                            }
                          }}
                        >
                          <Flex gap={2}>
                            <Input name="pair" placeholder="e.g., SOL/USDT" size="sm" bg="white" color="black" />
                            <Button type="submit" size="sm" colorScheme="gold" bg="gold" color="black">
                              Submit
                            </Button>
                          </Flex>
                        </form>
                      </Box>
                    </>
                  )}

                  {llmPage && (
                    <>
                      <Box bg="gray" p={4} rounded="md" minH="40vh">
                        {streaming ? <Spinner color="gold" /> : (
                          thinkingText ? (
                            <>
                              <Global
                                styles={`
                            @keyframes blink {
                              0%, 100% { opacity: 1; }
                              50% { opacity: 0.5; }
                            }
                          `}
                              />
                              <Text
                                whiteSpace="pre-wrap"
                                fontStyle="italic"
                                color="thinking"
                                animation="blink 1.5s ease-in-out infinite"
                              >
                                {thinkingText}
                              </Text>
                            </>
                          ) : <Box whiteSpace="pre-wrap">
                            <ReactMarkdown>{llmText}</ReactMarkdown>
                          </Box>
                        )}
                      </Box>
                    </>
                  )}
                </>
              )
          )
        }
      </Box>
    </Box>

  )
}