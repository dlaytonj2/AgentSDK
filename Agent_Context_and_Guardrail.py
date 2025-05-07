

import asyncio
from dataclasses import dataclass
from pydantic import BaseModel
from agents import Agent, RunContextWrapper, Runner, function_tool, input_guardrail, GuardrailFunctionOutput, InputGuardrailTripwireTriggered



import os
os.environ["OPENAI_API_KEY"]='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'

model="gpt-4o-mini"

# --- Classes  for structured outputs ---

class NumberAnalysis(BaseModel):
    is_valid: bool
    reasoning: str


# --- Context Class ---

@dataclass
class UserContext:  
    decimal_places: int = 4 
    thousands_separator: bool=True
    multiply_counter: int = 0 
    input_guardrail_reasoning: str = ''
    

# --- Tools ---
@function_tool
def multiply(wrapper: RunContextWrapper[UserContext], x: float, y: float) -> str:
    """Multiplies `x` and `y` to provide a precise
    answer and ensures that it is in the right format. North America or Europe"""
    
    result = x * y

    dp = wrapper.context.decimal_places
    thousands_separator = wrapper.context.thousands_separator
    ts = ''
    if thousands_separator:
        ts =','

    numeric_format = ts+'.'+str(dp)+'f'

    result_format = f"{result:{numeric_format}}"

    wrapper.context.multiply_counter += 1
    
    return result_format

# --- Guardrails ---

number_analyis_agent = Agent(
    name="Number Analyzer",
    instructions="""
    You analyze the prompt to ensure that it has two numbers and that the request is to multiply the two numbers
    """,
    output_type=NumberAnalysis,
    model=model
)

@input_guardrail
async def number_guardrail(ctx, agent, input_data):
    """Check if the prompt is valid for multiplication and two numbers are provided"""
    print(f'\n Inside guardrail: {agent.name}{agent.instructions}')
    try:
        analysis_prompt = f"Verify this request {input_data}."
        result = await Runner.run(number_analyis_agent, analysis_prompt)
        final_output = result.final_output_as(NumberAnalysis)
        
      
        print ('\n Final Output inside guardrail:',final_output,)
        if final_output.is_valid == False:
            ctx.context.input_guardrail_reasoning = final_output.reasoning
            

        return GuardrailFunctionOutput(
            output_info=final_output,
            # Trigger the tripwire if the input is not valid for multiplication
            tripwire_triggered = False if final_output.is_valid  else True,
            
        )
  
    except Exception as e:
        # Handle any errors gracefully
        print(e)
        return GuardrailFunctionOutput(
            output_info=NumberAnalysis(is_valid=True, reasoning=f"Error in analyzing the validity of the input: {str(e)}"),
            tripwire_triggered=False
        )


# --- Main Agent ---

multiply_agent = Agent [UserContext](
    name="Multiplier",
    instructions=(
    '''
    You're a helpful assistant, remember to always use the provided tools whenever possible. The output should be in plain text 
    and present the answer as plain numeric values without Markdown, LaTeX, or any special characters. 
    The result of the calculation should preserve the same number of decimal places as returned from any tools used.
    '''
    ),
    model=model,
    tools=[multiply],  # note that we expect a list of tools
    input_guardrails=[number_guardrail]

)

# Run as a non-streamed 

user_context = UserContext(
    decimal_places  = 4,
    thousands_separator =True,
    multiply_counter = 0, 
    input_guardrail_reasoning=''
    )

# main function 

async def main() -> None:

    try:
        result = await Runner.run(
        multiply_agent,
        input='''The is a very long text, that has nothing to do with multiplication but in the end I will ask you to multiply the 
        numbers Alpha and Beta. Go ahead and multiply them''',
        context=user_context
        )
    
        print('\n',result.final_output) 

      
    except InputGuardrailTripwireTriggered as e:

        print("\n ⚠️ GUARDRAIL TRIGGERED ⚠️")
        print('\n Reasoning: ',user_context.input_guardrail_reasoning)
    

if __name__ == "__main__":
    asyncio.run(main())









