import os
from typing import List, Dict, Any, Callable
from google import genai

class Agent:
    def __init__(self, name: str, system_prompt: str, tools: Dict[str, Callable], memory_module=None):
        self.name = name
        self.system_prompt = system_prompt
        self.tools = tools
        self.memory = memory_module
        
        # conversation history
        self.history = []
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            # print("API KEY IS MISSING!!") # debug
            raise ValueError("GEMINI_API_KEY environment variable not set. Please add it to your .env file.")
        
        # init gemini client... using the new standard SDK here
        self.client = genai.Client(api_key=api_key)
        
        # TODO: maybe let the user change the model later? flash is fast enough for now
        self.model_name = 'gemini-2.5-flash' 

    def _format_prompt(self, task: str) -> str:
        """Constructs the prompt including tool definitions and history."""
        tool_desc = ""
        for name, func in self.tools.items():
            tool_desc += f"- {name}: {func.__doc__}\n"
            
        final_prompt = f"{self.system_prompt}\n\nAvailable Tools:\n{tool_desc}\n\nTask: {task}"
        return final_prompt

    def run(self, task: str, max_steps: int = 15, on_step=None):
        """
        The main ReAct (Reason + Act) loop.
        """
        context = ""
        # grab past memory if we have the module loaded
        if self.memory:
            past_knowledge = self.memory.search(task)
            context = f"\n\nContext from previous research (Vector DB):\n{past_knowledge}\n"
            
        current_prompt = self._format_prompt(task + context)
        
        # push the first user prompt to the list
        self.history.append({"role": "user", "parts": [{"text": current_prompt}]})
        
        # start the loop!
        for step in range(max_steps):
            
            # call the model
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=self.history
            )
            
            text_response = response.text
            # print(f"Raw Output: {text_response}") # uncomment this to debug what the LLM is actually saying
            
            self.history.append({"role": "model", "parts": [{"text": text_response}]})
            
            if on_step:
                on_step("thought", text_response)

            # Check if Agent is done figuring it out
            if "Final Answer:" in text_response:
                # slice the string to get just the answer part
                answer_txt = text_response.split("Final Answer:")[-1].strip()
                
                # save memory so it remembers next time
                if self.memory:
                    self.memory.save(f"Task: {task}\nInsight: {answer_txt}")
                    
                return answer_txt

            # Parse out the Action
            if "Action:" in text_response and "Action Input:" in text_response:
                
                # hacky way to find the exact line but it works fine lol
                action_line = [line for line in text_response.split('\n') if line.startswith('Action:')][0]
                action_input_line = [line for line in text_response.split('\n') if line.startswith('Action Input:')][0]
                
                tool_name = action_line.replace("Action:", "").strip()
                tool_input = action_input_line.replace("Action Input:", "").strip()
                
                if on_step:
                    on_step("action", f"Running '{tool_name}' with input: '{tool_input}'")
                
                # Actually run the python function
                if tool_name in self.tools:
                    # try/except here just in case the scrape or search fails 
                    # so the whole loop doesn't instantly die
                    try:
                        observation_result = str(self.tools[tool_name](tool_input))
                    except Exception as e:
                        observation_result = f"Error executing {tool_name}: {e}"
                else:
                    observation_result = f"Error: Tool '{tool_name}' not found."
                    
                observation_string = f"Observation: {observation_result}"
                
                if on_step:
                    on_step("observation", observation_string)
                    
                # feed the tool result back into the history so the LLM can read it on the next loop
                self.history.append({"role": "user", "parts": [{"text": observation_string}]})
            else:
                # LLM forgot the format, yell at it to fix it
                # print("Agent messed up format")
                self.history.append({"role": "user", "parts": [{"text": "You must use the exact format: 'Thought: ...', 'Action: ...', 'Action Input: ...' OR output 'Final Answer: ...'"}]})

        # if it hits the step limit
        return "Agent stopped. Reached maximum number of steps without finding a Final Answer."
