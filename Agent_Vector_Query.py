import asyncio

from agents import Agent, FileSearchTool, Runner, trace

import textwrap
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# Set the API key from the environment
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

from pydantic import BaseModel 

class FileSearch_Report(BaseModel):
    short_summary: str
    """A short 2-3 sentence summary of the findings."""

    markdown_report: str
    """The final report"""

    follow_up_questions: list[str]
    """Suggested topics to research further"""

async def FileSearcher():

    vector_store_name = "JulesVerne"
    vector_store_id = 'vs_67f2bbb62ac8819192a1df7af9a1bf5f'

    agent = Agent(
        name="File searcher",
        instructions='''You are a helpful agent with expertise in literature. 
        You always read what has been provided from end to end before answering any questions
        You always come up with interesting topics to followup on''',
        model='gpt-4o',
        tools=[
            FileSearchTool(
                max_num_results=5,
                vector_store_ids=[vector_store_id],
                include_search_results=False)
        ],
        output_type=FileSearch_Report
    )
    
    # Create a second file search agent with different configuration
    agent2 = Agent(
        name="File searcher 2",
        instructions='''You are an analytical agent specializing in technical literature and research papers.
        You focus on extracting key technical concepts and methodologies from documents.
        You always provide specific citations when referencing content.
        You organize your analysis in a structured format with clear sections.
        You suggest related technical topics that might interest the user.''',
        model='gpt-4o',
        tools=[
            FileSearchTool(
                max_num_results=7,  # Increased result count
                vector_store_ids=[vector_store_id],
                include_search_results=True)  # Include raw results
        ],
        output_type=FileSearch_Report
    )
    
    query = """
    First, read the story carefully and identify who is the principal antagonist and 
    if there is no antagonist explain further."""
    
    with trace("File search Jules Verne"):
        result = await Runner.run(
            agent,query
        )

    FinalReport =(result.final_output)

    print('\n',textwrap.fill(FinalReport.short_summary, width=80))
    print('\n',textwrap.fill(FinalReport.markdown_report, width=80))
    print('\n', "Follow-up Questions:")

    
    DrilldownReports = []

    for question in FinalReport.follow_up_questions:
        print (f'\n Doing a deep dive on this follow-on question:\n {textwrap.fill(question, width=80)}...')
        result = await Runner.run(
            agent,question
        )
        DrilldownReport = result.final_output
        DrilldownReports.append(DrilldownReport)


    
    # Print a formatted summary of all drill-down reports after iterations
    print("\n\n===== SUMMARY OF ALL DRILL-DOWN REPORTS =====")
    for i, report in enumerate(DrilldownReports, 1):
        print(f"\n----- Report #{i} -----")
        print(f"Summary: {textwrap.fill(report.short_summary, width=80)}")
        print(f"\nFollow-up Questions:")
        for j, question in enumerate(report.follow_up_questions, 1):
            print(f"  {j}. {textwrap.fill(question, width=76)}")
        print("\n" + "-" * 40)
 
if __name__ == "__main__":
    asyncio.run(FileSearcher())

