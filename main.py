from orchestrator.orchestrator import Orchestrator
from models.models import Memory, State, PlannerInput, PlannerOutput, ExecutorInput, ExecutorOutput
from agent.agent import Agent
from prompts.prompts import planner_system_prompt, executor_system_prompt

if __name__ == "__main__":
    initial_memory = Memory(
        objective="Create a report on AI advancements in 2022",
        current_state=State.PLAN,
        task_list=[],
        current_task=None,
        final_response=None
    )

    state_to_agent_map = {
        State.PLAN: Agent(
            name = "planner",
            system_prompt=planner_system_prompt,
            input_format=PlannerInput,
            output_format=PlannerOutput, 
            keep_message_history=False
        ),
        State.EXECUTE: Agent(
            name = "executor",
            system_prompt=executor_system_prompt,
            input_format=ExecutorInput,
            output_format=ExecutorOutput,
            keep_message_history=False
        )
    }

    orchestrator = Orchestrator(initial_memory, state_to_agent_map=state_to_agent_map)
    final_memory = orchestrator.run()

    print(f"Final Response: {final_memory.final_response}")