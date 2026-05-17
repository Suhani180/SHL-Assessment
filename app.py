import gradio as gr

from app.main import app as fastapi_app

# -----------------------------------------------------
# OPTIONAL DEMO UI
# -----------------------------------------------------

def respond(message, history):

    return (
        "SHL conversational recommender "
        "API is running successfully."
    )

demo = gr.ChatInterface(
    fn=respond,
    title="SHL Assessment Recommender"
)

# -----------------------------------------------------
# MOUNT FASTAPI
# -----------------------------------------------------

app = gr.mount_gradio_app(
    fastapi_app,
    demo,
    path="/"
)