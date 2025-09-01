import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline


def load_mermaid_llama():
    MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, use_fast=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        device_map="auto",
        torch_dtype=torch.float32,
        low_cpu_mem_usage=True,
    )
    return pipeline("text-generation", model=model, tokenizer=tokenizer)


class DiagramAgent:
    def __init__(self):
        self.model = load_mermaid_llama()

    def correct_syntax(self, raw_code: str) -> str:
        prompt = f"""
    You are a Mermaid syntax expert. You will get a mermaid code as input, you have to correct all the sntax errors in that code. 
    Ensure it is syntactically correct and compatible with Mermaid version 10.9.3. 
    Return only the corrected Mermaid code enclosed in triple backticks.
    - Ensure the Mermaid syntax is correct
    - Do not use HTML entities like `&gt;` or `&lt;`—use raw Mermaid syntax (`-->`, `|label|`).
    *   EXTENSIVELY use Mermaid diagrams (e.g., \`flowchart TD\`, \`sequenceDiagram\`, \`classDiagram\`, \`erDiagram\`, \`graph TD\`) to visually represent architectures, flows, relationships, and schemas found in the source files.
    *   Ensure diagrams are accurate and directly derived from information in the \`[RELEVANT_SOURCE_FILES]\`.
    *   Provide a brief explanation before or after each diagram to give context.
    *   If the syntax is correct, do not change the original syntax.
    *   CRITICAL: All diagrams MUST follow strict vertical orientation:
       - Use "graph TD" (top-down) directive for flow diagrams
       - NEVER use "graph LR" (left-right)
       - Maximum node width should be 3-4 words
       - For sequence diagrams:
         - Start with "sequenceDiagram" directive on its own line
         - Define ALL participants at the beginning
         - Use descriptive but concise participant names
         - Use the correct arrow types:
           - ->> for request/asynchronous messages
           - -->> for response messages
           - -x for failed messages
         - Include activation boxes using +/- notation
         - Add notes for clarification using "Note over" or "Note right of"
    
    {raw_code}
    """
        print(raw_code)
        response = self.model(prompt)[0]["generated_text"]
        return response
