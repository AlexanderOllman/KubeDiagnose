import autogen
from typing import List, Dict

# Configure the agents
config_list = [
    {
        'model': 'gpt-4',
        'api_key': 'your-api-key-here'
    }
]

# Create assistant configurations
assistant_config = {
    "seed": 42,
    "temperature": 0.2,
    "config_list": config_list,
}

# Create the specialized agents
user_proxy = autogen.UserProxyAgent(
    name="User_Proxy",
    system_message="A human user who needs help diagnosing Kubernetes issues.",
    code_execution_config={"work_dir": "output"}
)

k8s_analyst = autogen.AssistantAgent(
    name="K8s_Analyst",
    system_message="""You are a Kubernetes expert analyst. Your role is to:
    1. Analyze the user's problem description
    2. Break down the issue into specific areas to investigate
    3. Suggest relevant areas to check
    4. Coordinate with the Command Generator for specific kubectl commands""",
    llm_config=assistant_config,
)

command_generator = autogen.AssistantAgent(
    name="Command_Generator",
    system_message="""You are a Kubernetes command specialist. Your role is to:
    1. Generate specific kubectl commands based on the analysis
    2. Ensure commands are safe to execute
    3. Provide explanation for each command
    4. Consider namespace context and cluster-wide implications""",
    llm_config=assistant_config,
)

def diagnose_kubernetes_issue(prompt: str) -> List[Dict]:
    """
    Process a natural language prompt and generate kubernetes diagnostic commands.
    """
    # Initialize the chat between agents
    groupchat = autogen.GroupChat(
        agents=[user_proxy, k8s_analyst, command_generator],
        messages=[],
        max_round=10
    )
    manager = autogen.GroupChatManager(groupchat=groupchat)

    # Start the conversation
    user_proxy.initiate_chat(
        manager,
        message=f"""
        Please help diagnose this Kubernetes issue:
        {prompt}
        
        Provide a list of kubectl commands to investigate and diagnose the problem.
        """
    )

    # Extract the relevant commands and explanations from the chat history
    # You might want to implement additional parsing logic here
    return groupchat.messages

# Example usage
if __name__ == "__main__":
    sample_prompt = "My application pods are constantly crashing and showing CrashLoopBackOff status"
    
    results = diagnose_kubernetes_issue(sample_prompt)
    
    # Print the diagnostic conversation and commands
    for message in results:
        print(f"\n{message['sender']}: {message['content']}")