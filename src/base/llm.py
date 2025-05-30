from utils.secret_manager import get_groq_key
from groq import Groq
from groq.types.chat.chat_completion_chunk import ChatCompletionChunk

from utils.langfuse import get_langfuse
from .action import BaseActionProtected


class BaseLLM(BaseActionProtected):
    def __init__(self, model: str = "llama3-70b-8192", langfuse_prompt: str = "crypto"):
        super().__init__()        
        self.client = Groq(api_key=get_groq_key().strip())
        self.model = model
        self.langfuse_prompt = langfuse_prompt
        self.prompt_template = get_langfuse().get_prompt(langfuse_prompt)

        
    
    
    def query(self, system_prompt: str, user_prompt: str, stream: bool = True):
        trace = get_langfuse().trace(name=f"{self.langfuse_prompt}-trace")
        messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        
        generation = trace.generation(
            name=f"{self.langfuse_prompt}-generation",
            model=self.model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
        )
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=stream
        )
        full_response = ""
        usage = None
        if stream:
            yield "\n\n"
            for chunk in response:
                chunk: ChatCompletionChunk
                if chunk.choices and chunk.choices[0].delta.content:            
                    if chunk.usage:
                        usage = chunk.usage
                    content_chunk = chunk.choices[0].delta.content
                    full_response += content_chunk            
                    yield content_chunk
        else:
            full_response = response.choices[0].message.content
            if response.usage:
                usage = response.usage
            
                
        generation.end(
            output=full_response,
            usage=usage,   
        )

        trace.update()
        if not stream:
            return full_response
            
        
            