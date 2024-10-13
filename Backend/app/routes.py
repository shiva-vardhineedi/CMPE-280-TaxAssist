from fastapi import APIRouter, Request, Query
from fastapi.responses import JSONResponse
from app.anthropic_api import get_claude_response_with_history
from app.db import save_to_db, get_history

# Create an APIRouter instance for managing routes
tax_router = APIRouter()

@tax_router.post("/get-tax-response")
async def get_tax_response(request: Request, history: bool = Query(False)):
    data = await request.json()
    user_input = data.get("user_input", "")

    # Get the last 5 conversations from the history if history=true
    conversation_history = []
    if history:
        conversation_history = get_history(5)  # Fetch last 5 or fewer interactions

    print(conversation_history)

    # Get the response from Claude-3 model, including history if applicable
    response_text = get_claude_response_with_history(user_input, conversation_history)
    print(f"Response text: {response_text}")

    # Save the user input and the assistant's response to the database
    save_to_db(user_input, response_text)

    # Return the response as JSON
    return JSONResponse(content={"response": response_text})

@tax_router.get("/get-history/")
async def get_history_api(context_window: int = 5):
    """
    Get the last N interactions from the chat history.
    """
    history = get_history(context_window)
    history_data = [{"prompt": h[0], "response": h[1]} for h in history][::-1]
    return JSONResponse(content={"history": history_data})
