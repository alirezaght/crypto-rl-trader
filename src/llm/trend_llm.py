from base.llm import BaseLLM

class TrendLLM(BaseLLM):
    
    def __init__(self):
        super().__init__(langfuse_prompt="trend")
        
        
    def query_llm(self, trends: list):
        system_prompt = self.prompt_template.compile(
            TRENDS=trends,            
        )
        user_prompt = f"Give me the trends in crypto and stock markets."
        yield from self.query(system_prompt, user_prompt)