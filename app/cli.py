"""Interactive Command-Line Runner for Local Testing."""
import sys
from app.agents.root_supervisor import root_supervisor

def main():
    print("=" * 70)
    print("  Enterprise HR & IT Agentic Assistant (Google ADK Runtime)")
    print("  Type 'exit' or 'quit' to stop.")
    print("=" * 70)
    
    user_id = "EMP-1049"
    while True:
        try:
            prompt = input(f"\n[{user_id}] > ")
            if prompt.strip().lower() in ["exit", "quit"]:
                break
            if not prompt.strip():
                continue
                
            res = root_supervisor.execute_turn(user_id=user_id, user_prompt=prompt)
            print(f"\n[Assistant]:\n{res['response']}")
            if res.get("tool_calls"):
                print(f"\n(Executed {len(res['tool_calls'])} tool call(s))")
        except (KeyboardInterrupt, EOFError):
            break
            
    print("\nSession ended.")

if __name__ == "__main__":
    main()
