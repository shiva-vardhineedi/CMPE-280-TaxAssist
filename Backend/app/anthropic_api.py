import os
import anthropic

# Get API key from environment variables
api_key = os.getenv("ANTHROPIC_API_KEY")

# Ensure the API key is available
if not api_key:
    raise ValueError("Anthropic API key not found. Please set ANTHROPIC_API_KEY environment variable.")

# Create the client using the API key
client = anthropic.Anthropic(api_key=api_key)

def build_conversation_history(history):
    """
    Build conversation history in the format required by Anthropics API.
    Each entry is a tuple of (user, assistant).
    """
    messages = []
    for prompt, response in history:
        messages.append({"role": "user", "content": [{"type": "text", "text": prompt}]})
        messages.append({"role": "assistant", "content": [{"type": "text", "text": response}]})
    return messages

def get_claude_response_with_history(user_input: str, history: list) -> str:
    """
    Send a tax-related query to Claude-3 including conversation history if provided.
    """
    # Build the conversation history
    conversation = build_conversation_history(history)

    extra_inputs = [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "HI what is your view on KMP search algorithm?"
                }
            ]
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "Not Tax Related. Sorry!"
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Okay, I made $60,000 last year, how much tax do I need to pay?"
                }
            ]
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "Thank you for your tax question. Based on your income of $60,000, the tax amount depends on several factors like your filing status and any deductions. Could you share your filing status (e.g., single, married) and any applicable deductions or credits?"
                }
            ]
        },
        {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": user_input  # User's new input is dynamic here
            }
        ]
    }]

    # Add the new user input to the conversation
    for item in extra_inputs:
        conversation.append(item)

    # Send the request to GPT
    message = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1000,
        temperature=0,
        system=(
            "You are a Tax Filing Assistant who strictly answers only tax-related questions. "
            "Never answer questions or provide information that is not related to taxes. "
            "If a user asks an off-topic or irrelevant question, simply respond by informing them that you only provide tax-related assistance and firmly redirect them to tax-related topics. "
            "Under no circumstances should you respond to or engage with non-tax-related topics.\n\n"
            "- If the user asks for tax advice or calculations, guide them through the necessary details (e.g., income, filing status, deductions, tax credits) and give estimates where appropriate.\n"
            "- Keep your responses concise and ensure that you stay within the tax-related scope at all times. If the question is irrelevant, state clearly that you only handle tax-related queries.\n"
            "- Be firm but polite if the user insists on off-topic discussions. Politely explain that you are a tax assistant and are unable to discuss non-tax topics.\n\n"
            "Your main goal is to help users with tax-related queries, calculations, deductions, credits, and filing. Any other questions must be ignored, and the user should be redirected to tax matters."
        ),
        messages=conversation
    )

    # Extract the text from TextBlock objects
    response_text = ""
    if isinstance(message.content, list) and len(message.content) > 0:
        response_text = "\n".join([block.text for block in message.content if hasattr(block, 'text')])

    return response_text
