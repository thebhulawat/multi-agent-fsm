from models.models import Memory, State, Task, PlannerInput, PlannerOutput, ExecutorInput, ExecutorOutput
from agent.agent import Agent
from colorama import Fore, init
import textwrap

init(autoreset=True)

class Orchestrator:
    def __init__(self, memory: Memory, state_to_agent_map: dict[State, Agent]):
        self.state_to_agent_map = state_to_agent_map
        self.memory = memory

    def run(self) -> Memory:
        while self.memory.current_state != State.COMPLETED:
            self._handle_state()

        self._print_final_response(self.memory)
        return self.memory

    def _handle_state(self):
        current_state = self.memory.current_state
        if current_state not in self.state_to_agent_map: 
            raise ValueError(f"Unhandled state! No agent for {current_state}")
    
        if current_state == State.PLAN:
            self._handle_planner()
        elif current_state == State.EXECUTE:
            self._handle_executor()
        else:
            raise ValueError(f"Unhandled state: {current_state}")
        
    def _handle_planner(self):
        agent = self.state_to_agent_map[State.PLAN]
        self._print_memory_and_agent(self.memory, agent.name)
    
        input_data = PlannerInput(
            objective=self.memory.objective,
            task_for_review=self.memory.current_task,
            completed_tasks=[task for task in self.memory.task_list if task.result]
            )
        
        output = agent.invoke(input_data)
        
        self._update_memory_from_planner(self.memory, output)
        
        print(f"{Fore.MAGENTA}Planner has updated the memory.")

    
    def _handle_executor(self):
        agent = self.state_to_agent_map[State.EXECUTE]
        self._print_memory_and_agent(self.memory, agent.name)
    
        input_data = ExecutorInput(task=self.memory.current_task)
        
        output: ExecutorOutput = agent.invoke(input_data)

        self._print_task_result(output.completed_task)
        
        self._update_memory_from_executor(self.memory, output)
        
        print(f"{Fore.MAGENTA}Executor has completed a task.")
        

    
    def _update_memory_from_planner(self, memory: Memory, planner_output: PlannerOutput):
        if planner_output.is_complete:
            memory.current_state = State.COMPLETED
            memory.final_response = planner_output.final_response
        elif planner_output.next_task:
            memory.current_state = State.EXECUTE
            next_task_id = len(memory.task_list) + 1
            memory.current_task = Task(id=next_task_id, description=planner_output.next_task.description, result=None)
            memory.task_list.append(memory.current_task)
        else:
            raise ValueError("Planner did not provide next task or completion status")

    
    def _update_memory_from_executor(self, memory: Memory, executor_output: ExecutorOutput):
        for task in memory.task_list:
            if task.id == executor_output.completed_task.id:
                task.result = executor_output.completed_task.result
                break
        memory.current_task = None
        memory.current_state = State.PLAN

    
    def _print_memory_and_agent(self, memory: Memory, agent_type: str):
        print(f"{Fore.CYAN}{'='*50}")
        print(f"{Fore.YELLOW}Current State: {Fore.GREEN}{memory.current_state}")
        print(f"{Fore.YELLOW}Agent: {Fore.GREEN}{agent_type}")
        if memory.current_task:
            print(f"{Fore.YELLOW}Current Task: {Fore.GREEN}{memory.current_task.description}")
        print(f"{Fore.YELLOW}Task List:")
        for task in memory.task_list:
            status = "✓" if task.result else " "
            print(f"{Fore.GREEN}  [{status}] {task.description}")
        print(f"{Fore.CYAN}{'='*50}")

    
    def _print_task_result(self, task: Task):
        print(f"{Fore.CYAN}{'='*50}")
        print(f"{Fore.YELLOW}Task Completed: {Fore.GREEN}{task.description}")
        print(f"{Fore.YELLOW}Result:")
        wrapped_result = textwrap.wrap(task.result, width=80)
        for line in wrapped_result:
            print(f"{Fore.WHITE}{line}")
        print(f"{Fore.CYAN}{'='*50}")

    
    def _print_final_response(self, memory: Memory):
        print(f"\n{Fore.GREEN}{'='*50}")
        print(f"{Fore.GREEN}Objective Completed!")
        print(f"{Fore.GREEN}{'='*50}")
        print(f"{Fore.YELLOW}Final Response:")
        wrapped_response = textwrap.wrap(memory.final_response, width=80)
        for line in wrapped_response:
            print(f"{Fore.WHITE}{line}")
        print(f"{Fore.GREEN}{'='*50}")