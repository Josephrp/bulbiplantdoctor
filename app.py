import gradio as gr
import openai
from dotenv import load_dotenv
import os
import time

examples = [
    ["My Eucalyptus tree is struggling outside in the cold weather in europe"],
    ["My callatea house plant is yellowing."],
    ["We have a catcus as work that suddently started yellowing and wilting."]
]

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
assistant_id=os.getenv('ASSISTANT_ID')
client = openai.OpenAI(api_key=openai.api_key)

def ask_openai(question):
    try:
        thread = client.beta.threads.create()

        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=question,
        )

        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id
        )

        response_received = False
        timeout = 150
        start_time = time.time()

        while not response_received and time.time() - start_time < timeout:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id,
            )
            if run_status.status == 'completed':
                response_received = True
            else:
                time.sleep(4)  

        if not response_received:
            return "Response timed out."

        steps = client.beta.threads.runs.steps.list(
            thread_id=thread.id,
            run_id=run.id
        )

        if steps.data:
            last_step = steps.data[-1]
            if last_step.type == 'message_creation':
                message_id = last_step.step_details.message_creation.message_id
                message = client.beta.threads.messages.retrieve(
                    thread_id=thread.id,
                    message_id=message_id
                )
                if message.content and message.content[0].type == 'text':
                    return message.content[0].text.value
        return "No response."
        
    except Exception as e:
        return f"An error occurred: {str(e)}"

iface = gr.Interface(
    fn=ask_openai,
    inputs=gr.Textbox(lines=5, placeholder="Hi there, I have a plant that's..."),
    outputs=gr.Markdown(),
    title="Wecome to Tonic's Bulbi Plant Doctor",
    description="""Introduce your plant below. Be as descriptive as possible. Respond with additional information when prompted. Save your plants with Bulbi Plant Doctor""",
    examples=examples
)

iface.launch()