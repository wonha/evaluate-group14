"""Google ADK Agent Web & Runtime Entrypoint."""
from app.agents.root_supervisor import root_supervisor

# Standard Google ADK exports for 'adk web' discovery
agent = root_supervisor
root_agent = root_supervisor

if __name__ == '__main__':
    from app.cli import main
    main()
