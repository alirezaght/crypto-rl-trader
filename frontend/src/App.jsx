import React, { useEffect, useState } from 'react'
import {
  Box,
  Heading,
  Input,
  Button,
  Text,
  VStack,
  Code,
  ChakraProvider,
  Divider,
} from '@chakra-ui/react'
import { initializeApp } from 'firebase/app'
import {
  getAuth,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  signInWithPopup,
  GoogleAuthProvider,
  onAuthStateChanged,
} from 'firebase/auth'

const firebaseConfig = {
  apiKey: "AIzaSyBr3tD3w8_35ouHIXbtC0mHbzFl-LZqCZ0",
  authDomain: "silver-treat-456607-e6.firebaseapp.com",
  projectId: "silver-treat-456607-e6",
  storageBucket: "silver-treat-456607-e6.firebasestorage.app",
  messagingSenderId: "327272059000",
  appId: "1:327272059000:web:68fc9edea7ff1877ff1d8d",
  measurementId: "G-ZY38R9FRE4"
}

const app = initializeApp(firebaseConfig)
const auth = getAuth(app)
const googleProvider = new GoogleAuthProvider()

const actionMap = {
  0: "🟡 Hold",
  1: "🟢 Buy (<25% expected rise)",
  2: "🟢 Buy (25–50% expected rise)",
  3: "🟢 Buy (>50% expected rise)",
  4: "🔴 Sell (<25% expected drop)",
  5: "🔴 Sell (25–50% expected drop)",
  6: "🔴 Sell (>50% expected drop)",
}

export default function App() {
  const [user, setUser] = useState(null)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [isLogin, setIsLogin] = useState(true)
  const [apiResponse, setApiResponse] = useState(null)

  useEffect(() => {
    return onAuthStateChanged(auth, (user) => {
      setUser(user)
      setApiResponse(null)
    })
  }, [])

  const handleAuth = async () => {
    try {
      setLoading(true)
      if (isLogin) {
        await signInWithEmailAndPassword(auth, email, password)
      } else {
        const result = await createUserWithEmailAndPassword(auth, email, password)
        await fetchPrediction(result.user)
      }
    } catch (err) {
      alert(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleLogin = async () => {
    try {
      setLoading(true)
      const result = await signInWithPopup(auth, googleProvider)
      await fetchPrediction(result.user)
    } catch (err) {
      alert(`Google login failed: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const fetchPrediction = async (firebaseUser = user) => {
    try {
      setLoading(true)
      const token = await firebaseUser.getIdToken()
      const response = await fetch(`https://tradepulse-api-327272059000.europe-west1.run.app/predict?symbol=BTC/USD`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      const data = await response.json()
      setApiResponse(data)
    } catch (err) {
      setApiResponse({ error: err.message })
    } finally {
      setLoading(false)
    }
  }

  return (
    <ChakraProvider>
      <Box minH="100vh" bg="gray.50" p={6} display="flex" alignItems="center" justifyContent="center">
        <Box bg="white" p={8} rounded="xl" shadow="xl" maxW="lg" w="full">
          <VStack spacing={4} align="stretch">
            <Heading size="lg" textAlign="center">📈 TradePulse</Heading>

            {user ? (
              <>
                <Text textAlign="center">Logged in as <strong>{user.email}</strong></Text>
                <Button colorScheme="blue" onClick={() => fetchPrediction()} isLoading={loading}>
                  Get Prediction
                </Button>
                {apiResponse && (
                  <Box bg="gray.100" p={4} rounded="md">
                    <Text fontSize="sm" mb={1}>API Response:</Text>
                    <Code p={2} fontSize="sm">{JSON.stringify(apiResponse, null, 2)}</Code>
                    {typeof apiResponse.action === 'number' && (
                      <Text fontWeight="bold" mt={2}>{actionMap[apiResponse.action]}</Text>
                    )}
                  </Box>
                )}
                <Button variant="link" colorScheme="red" onClick={() => signOut(auth)}>Sign out</Button>
              </>
            ) : (
              <>
                <Input placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
                <Input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} />
                <Button colorScheme="blue" onClick={handleAuth} isLoading={loading}>
                  {isLogin ? "Login" : "Sign Up"}
                </Button>

                <Divider />
                <Button colorScheme="green" onClick={handleGoogleLogin} isLoading={loading}>
                  Continue with Google
                </Button>

                <Button variant="link" onClick={() => setIsLogin(!isLogin)}>
                  {isLogin ? "New here? Create an account" : "Already have an account? Login"}
                </Button>
              </>
            )}
          </VStack>
        </Box>
      </Box>
    </ChakraProvider>
  )
}