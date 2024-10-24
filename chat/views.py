import markdown
import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

from django.shortcuts import render, redirect
from .models import Message

md = markdown.Markdown(extensions=["fenced_code"])

def chat_view(request):
    nlimit = 3
    messages = Message.objects.all().order_by('-id')[:nlimit]
    return render(request, 'chat/chat.html', {'messages': messages})

def add_conversation(request):
    
    user_message = request.POST.get('message')
    bot_message = get_ai_response(user_message)
    Message.objects.create(user_message=user_message, bot_message=bot_message)
    messages = Message.objects.all()
    return render(request, 'chat/partials/_chat_box.html', {'messages': messages})

def clear_chat(request):
    Message.objects.all().delete()
    messages = Message.objects.all()
    return redirect('chat_view')

def convert_markdown(resp):
    #markdown_content = resp.objects.first()
    resp = md.convert(resp)
    return resp

def get_ai_response(user_input: str) -> str:
    # get all messages from the database
    messages = get_existing_messages()
    messages.append({
        "role": "system", "content": "You are a helpful assistant",
        "role": "user", "content": f"{user_input}"})
    
    # initialise the client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # deployment_name="gpt4" 
    model = "gpt-4o-mini"    
    response = client.chat.completions.create(model=model, messages=messages)

    ai_message = response.choices[0].message.content
    converted_ai_message = convert_markdown(ai_message)
    return converted_ai_message


def get_existing_messages() -> list:
    """
    Get all messages from the database and format them for the API.
    """
    formatted_messages = []

    for message in Message.objects.values('user_message', 'bot_message'):
        formatted_messages.append({"role": "user", "content": message['user_message']})
        formatted_messages.append({"role": "assistant", "content": message['bot_message']})

    return formatted_messages