import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware  # Import CORS middleware
from dotenv import load_dotenv  # Import dotenv to load environment variables from .env file
import anthropic

# Load environment variables from a .env file if it exists
load_dotenv()

app = FastAPI()

# Allow CORS (this enables cross-origin requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (POST, GET, etc.)
    allow_headers=["*"],  # Allow all headers, or specify allowed headers
)

# Get the API key from the environment variable
api_key = os.getenv("ANTHROPIC_API_KEY")

# Ensure the API key is available
if not api_key:
    raise ValueError("Anthropic API key not found. Please set ANTHROPIC_API_KEY environment variable.")

# Create the client using the API key from the file
client = anthropic.Anthropic(api_key=api_key)

@app.post("/get-tax-response")
async def get_tax_response(request: Request):
    data = await request.json()
    user_input = data.get("user_input", "")

    # Prepare the messages to ensure they are tax-focused
    messages = [
        {
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
                    "text": "I am filing as single and I have a standard deduction of $12,950. No other credits or deductions."
                }
            ]
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "For a single filer with a standard deduction of $12,950, your taxable income would be $60,000 - $12,950 = $47,050. Here is an estimated breakdown of your federal tax liability based on 2023 tax brackets:\\n\\n- 10% on the first $11,000 = $1,100\\n- 12% on the next $33,725 = $4,047\\n- 22% on the remaining $2,325 = $511.50\\n\\nTotal estimated federal tax = $1,100 + $4,047 + $511.50 = $5,658.50\\n\\nNote: This is an estimate, and state taxes or other factors may affect your total liability. Let me know if you'd like further details or have more tax-related questions!"
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Thanks! Also, can you explain what the child tax credit is?"
                }
            ]
        },
        {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "The Child Tax Credit is a tax benefit for families with qualifying dependent children under the age of 17. For tax year 2023, the credit can be up to $2,000 per child, depending on your income level. The credit is partially refundable, which means even if you owe less tax than the credit, you might still receive a portion of the remaining credit as a refund. Would you like to know if you qualify for this credit or how it affects your overall tax liability?"
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": user_input  # Dynamic input from user
                }
            ]
        }
    ]

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
        messages=messages
    )


    print("message.content structure:", message.content)

    # Extract the text from TextBlock objects
    response_text = ""
    if isinstance(message.content, list) and len(message.content) > 0:
        # Assuming message.content contains a list of TextBlocks, extract the 'text' field
        response_text = "\n".join([block.text for block in message.content if hasattr(block, 'text')])

    # Return the response as JSON
    return JSONResponse(content={"response": response_text})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
