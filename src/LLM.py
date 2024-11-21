from openai import OpenAI
from dotenv import load_dotenv
import src.prompt as prompts
import json

load_dotenv(override=True)

class LLM():
    def __init__(self, codeTree, model_name='gpt-4o-mini'):
        self.model = OpenAI()
        self.model_name = model_name

        self.messages = []
        self.codeTree = codeTree

        self._append('system', 
                     prompts.SYSTEM_PROMPT.format(REPO_TREE=self.codeTree.repoTree))
        
        f = open('src/tools.json', 'r')
        self.tools = json.load(f)

    def call(self, prompt=None, filepath=None, tool_choice='auto'):

        if filepath: 
            self._append('user', prompts.GENERATION_PROMPT.format(filepath=filepath))
        
        if prompt:  
            self._append('user', prompt)

        completion = self.model.chat.completions.create(
                        model=self.model_name,
                        messages=self.messages,
                        tools = self.tools,
                        tool_choice=tool_choice
                    )
        
        response = completion.choices[0].message.content

        self._append('assistant', str(response))

        tool_calls = completion.choices[0].message.tool_calls
        
        if tool_calls:
            self.messages.append(completion.choices[0].message)
            return self.function_call(tool_calls)
        else:
            return response
    
    def _append(self, role: str, content: str):
        self.messages.append({'role': role,
                              'content': str(content)})

    def function_call(self, tool_calls):
        for tool_call in tool_calls:
            if tool_call.function.name == 'retriever':
                function_args = json.loads(tool_call.function.arguments)
                filepath = function_args.get('filepath')

                function_response = self.codeTree.get(filepath)

                self.messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": tool_call.function.name,
                    "content": function_response,
                })
                
        return self.call(tool_choice='auto')
    
