"""Lab 12 (chapter 12): the loop behind tool use and ReAct, with a scripted stand-in for the model.

A real agent asks a language model what to do next. To keep this lab offline and free, `fake_model` is a
hand-written function that plays that role. Everything else (parsing the model's text, running the tool,
feeding the result back) is the real loop.

Run:  python lab12-tool-loop.py
"""
import re


def calculator(expression: str) -> str:
    if not re.fullmatch(r"[0-9+\-*/(). ]+", expression):  # never run arbitrary text
        return "error: only numbers and + - * / ( ) are allowed"
    return str(eval(expression))  # safe here only because of the check above


TOOLS = {"calculator": calculator}


def fake_model(transcript: str) -> str:
    """Stands in for an LLM. Real models produce text like this when prompted in the ReAct style."""
    if "Observation:" not in transcript:
        return "Thought: I should compute this instead of guessing.\nAction: calculator[1234 * 5678]"
    result = transcript.rsplit("Observation:", 1)[1].strip()
    return f"Thought: I have the result.\nFinal Answer: {result}"


question = "What is 1234 times 5678?"
transcript = f"Question: {question}\n"
for turn in range(5):  # always cap the number of turns
    reply = fake_model(transcript)
    transcript += reply + "\n"
    print(f"--- model turn {turn + 1} ---\n{reply}")
    final = re.search(r"Final Answer: (.*)", reply)
    if final:
        print(f"\nanswer: {final.group(1)}")
        break
    action = re.search(r"Action: (\w+)\[(.*)\]", reply)
    if not action or action.group(1) not in TOOLS:
        print("the model asked for a tool that does not exist; stopping")
        break
    observation = TOOLS[action.group(1)](action.group(2))
    print(f"[the program ran {action.group(1)} and got: {observation}]")
    transcript += f"Observation: {observation}\n"
