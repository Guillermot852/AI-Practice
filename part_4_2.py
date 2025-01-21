from dotenv import load_dotenv
import os
from groq import Groq
import re 

load_dotenv()
API_KEY = os.getenv('GROQ_API_KEY1')


client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Explain the importance of fast language models",
        }
    ],
    model="llama3-8b-8192",
)

# print(chat_completion.choices[0].message.content)

class Agent:
    def __init__(self, client, system):
        self.client = client #Groq(api_key=API_KEY)
        self.system = system
        self.messages = []
        if self.system:
            self.messages.append({"role": "system", "content": self.system})    

    def __call__(self, message=""):
        if message:
            self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result

    def execute(self):
        completion = client.chat.completions.create(
                    messages=self.messages,
                    model="llama3-70b-8192",
                )
        return completion.choices[0].message.content
    

system_prompt = """
    You run in a loop of Thought, Action, PAUSE, Observation.
    At the end of the loop you output an Answer
    Use Thought to describe your thoughts about the question you have been asked.
    Use Action to run one of the actions available to you - then return PAUSE.
    Observation will be the result of running those actions.

    Your available actions are:

    calculate:
    e.g. calculate: 4 * 7 / 3
    Runs a calculation and returns the number - uses Python so be sure to use floating point syntax if necessary

    get_planet_mass:
    e.g. get_planet_mass: Earth
    Returns the mass of the planet in kg

    Example session:

    Question: What is the mass of Earth times 2?
    Thought: I need to find the mass of Earth
    Action: get_planet_mass: Earth
    PAUSE

    You will be called again with this:

    Observation: 5.972e+24

    Thought: I need to multiply this by 2
    Action: calculate: 5.972e+24 * 2
    PAUSE

    You will be called again with this:
    Observation: 1.1944e+25

    If you have the answer, output it as the Answer. If you need to ask a question, output it as the Question.

    You then output:

    Answer: The mass of Earth times 2 is 1.1944e+25

    Now it's your turn!
""".strip()
    
# tools
def calculate(operation):
    return eval(operation)

def get_planet_mass(planet):
    masses = {
        "earth": 5.972e24,
        "mars": 6.39e23,
        "uupiter": 1.898e27,
        "saturn": 5.683e26,
        "uranus": 8.681e25,
        "neptune": 1.024e26,
        "mercury": 3.285e23,
        "venus": 4.867e24
    }
    return masses[planet.lower().strip()]


def agent_loop(max_iterations, system, query):
    agent = Agent(client, system_prompt)
    tools = ['calculate', 'get_planet_mass']
    next_prompt = query
    i = 0   
    while i < max_iterations:
        i += 1 
        result = agent(next_prompt)
        print(result)
        if "PAUSE" in result and "Action" in result:
            action = re.findall(r"Action: ([a-z_]+): (.+)", result, re.IGNORECASE) 
            chosen_tool = action[0][0]
            arg = action[0][1]

            if chosen_tool in tools:
                result_tool = eval(f"{chosen_tool}('{arg}')")
                next_prompt = f"Observation: {result_tool}"

            else: 
                next_prompt = f"Observation: Tool not found"
            print(next_prompt)
            continue

        if "Answer" in result:
            break


if __name__ == "__main__":
    agent_loop(max_iterations=5, system=system_prompt, query="What is the mass of Earth plus the mass of Mercury and all of it times 5?")
