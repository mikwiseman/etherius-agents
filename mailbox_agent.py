from uagents import Agent, Context, Model
 
class Message(Model):
    message: str
 
SEED_PHRASE = "mailbox282828"
 
# Now your agent is ready to join the Agentverse!
agent = Agent(
    name="mailbox282828",
    port=8028,
    mailbox=True        
)
 
# Copy the address shown below
print(f"Your agent's address is: {agent.address}")
 
if __name__ == "__main__":
    agent.run()