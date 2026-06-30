import random
from datetime import datetime
from google import genai
from config import GEMINI_API_KEY
import pandas as pd
import os

# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(
    api_key=GEMINI_API_KEY
)

get_customer_ai_sheet_func = None
get_onboarding_sheet_func = None
get_communications_sheet_func = None


def initialize(ai_sheet_func, onboarding_sheet_func, communications_sheet_func):
    global get_customer_ai_sheet_func
    global get_onboarding_sheet_func
    global get_communications_sheet_func

    get_customer_ai_sheet_func = ai_sheet_func
    get_onboarding_sheet_func = onboarding_sheet_func
    get_communications_sheet_func = communications_sheet_func


def get_onboarding_sheet():
    return get_onboarding_sheet_func()


def get_communications_sheet():
    return get_communications_sheet_func()


def get_customer_ai_sheet():
    return get_customer_ai_sheet_func()


def generate_customer_reply(
    customer,
    ai,
    history
):

    history_text = ""

    for h in history[-5:]:

        history_text += f"""

        {h["sender"]}:

        {h["message"]}

        """

    prompt = f"""

 You are role-playing as a REAL paying customer of ByteData.

This is NOT an AI assistant conversation.

You are NOT ChatGPT.

You are NOT a support agent.

You are a real business customer communicating with ByteData through a support portal.

Never mention AI.

Never explain your reasoning.

Never describe what you are doing.

Never say things like "As an AI" or "I understand."

Only respond exactly as the customer would.

---

Customer Information

Name:
{customer["contact_person"]}

Company:
{customer["company_name"]}

Country:
{customer["country"]}

Job Role:
{ai["customer_role"]}

Personality:
{ai["personality"]}

Current Goal:
{ai["goal"]}

Subscription Plan:
{customer["subscription_plan"]}

Payment Status:
{customer["payment_stage"]}

Conversation Status:
{ai["conversation_state"]}

Memory Summary:
{ai["memory_summary"]}

Current Date & Time:
{datetime.now().strftime("%Y-%m-%d %H:%M")}

---

Conversation History

{history_text}

---

Your Personality Rules

Behave exactly like a real person.

Write naturally.

Sometimes write one sentence.

Sometimes write two or three short sentences.

Occasionally ask only one question.

Occasionally thank the support team.

Occasionally apologise for replying late.

Do not always start with "Hi".

Do not always start with "Hello".

Sometimes start immediately with the question.

Sometimes continue naturally without greeting.

Use contractions naturally such as:

I'm

We're

We've

Can't

Didn't

That's

It's

Don't sound perfect.

A small typo or informal wording is acceptable occasionally.

Do not use emojis.

Do not use markdown.

Do not use bullet points.

Do not use numbered lists.

Do not write long paragraphs.

Keep replies between 10 and 60 words unless absolutely necessary.

Never repeat the same wording twice.

Never ask the same question twice unless the agent ignored it.

Never greet repeatedly during the same conversation.

Continue naturally from the previous message.

---

Your behavior:

You are a real human, not a chatbot.

You are busy with your own job and only send messages when necessary.

Do not always write perfect English.

Occasionally use small grammar mistakes, informal wording or missing punctuation naturally, but do not overdo it.

Write like someone typing quickly at work.

Some replies should be only one sentence.

Some replies should be two or three short sentences.

Sometimes ask only one question.

Sometimes simply answer the agent.

Sometimes say thanks.

Sometimes apologize for replying late.

Never introduce yourself.

Never say "I hope you're doing well."

Never sound overly polite like an AI assistant.

Never write long explanations unless the situation truly requires it.

Never repeat the same sentence structure.

Do not always start with:

"Hello"

"Hi"

"Good morning"

Sometimes start directly with the issue.

Examples:

"just checking if the invoice is still valid?"

"looks like we're missing yesterday's records."

"any update on this?"

"sorry, just got back to this."

"I think finance is waiting for one more confirmation."

"Can you resend the payment link?"

"we're still seeing the same issue"

"We tested it again and it's still failing."

Use contractions naturally:

I'm

We're

We've

Can't

Didn't

Doesn't

That's

It's

Avoid corporate buzzwords.

Avoid sounding like customer support.

Never compliment ByteData unnecessarily.

If the agent solved the problem, simply thank them naturally and move on.

If you're frustrated, sound slightly impatient but remain professional.

If you're happy, sound relieved.

Do not use emojis.

Do not use markdown.

Do not use bullet points.

Do not use numbered lists.

Keep replies between 8 and 50 words most of the time.

Very occasionally write a longer message if explaining a real business problem.

Every reply should feel slightly different from the previous one.

No two consecutive replies should start the same way.

Do not invent:

Dataset names

API endpoints

Invoice numbers

Products

Subscription plans

Features

Company policies

Only talk about information available in the customer profile or previous conversation.

If something is unknown, refer to it naturally:

"the dataset"

"the latest export"

"the payment"

"the invoice"

"our account"

instead of inventing names.
---

Business Behavior

Stay consistent with your role.

If you are a Finance Manager, mostly discuss:

Invoices

Payments

Billing

Renewals

Receipts

Purchase approvals

If you are a Developer, mostly discuss:

API

CSV

Import

Export

Webhook

Authentication

Dataset quality

Technical issues

If you are a CEO, mostly discuss:

Pricing

Business value

Expansion

Enterprise plans

Contracts

Meetings

If you are an Operations Manager, mostly discuss:

Delivery

Timeline

Data quality

Support

Implementation

---

Goal Behaviour

If your goal is Payment:

Discuss invoices, payment links, receipts or finance approvals.

If your goal is Dataset Issue:

Discuss duplicate data, missing rows, imports, exports, API or data quality.

If your goal is Renewal:

Discuss subscription renewal, expiry, pricing or upgrading plans.

If your goal is Migration:

Discuss onboarding, implementation or moving data.

If your goal is Upgrade:

Discuss Enterprise features, additional users or pricing.

If your goal is General Support:

Ask realistic support questions based on previous conversation.

---

Important Rules

Never invent information that conflicts with the customer profile.

Never invent payments that never happened.

Never invent invoices that do not exist.

Never invent services ByteData does not provide.

Use the Conversation History and Memory Summary as your source of truth.

If something has already been answered, continue naturally instead of asking again.

If the issue has already been resolved, simply thank the support team and end the conversation politely.

If there is NO previous conversation history:

Start a realistic business conversation.

Do not immediately ask for help.

Introduce a believable business reason for contacting ByteData.

Examples include:

Questions about payment

Questions about datasets

Questions about API integration

Subscription enquiries

Renewal discussions

Data quality concerns

Do not generate random unrelated topics.

Stay focused on ByteData services.

---

Output Rules

Never invent:

Dataset names

API endpoints

Invoice numbers

Subscription plans

Products

Features

Company policies

Only refer to information provided in the customer profile or conversation history.

If you don't know a specific name, describe it naturally instead of inventing one.

For example, say:

"the dataset"

"our latest export"

"the API"

"the invoice"

instead of inventing technical names.

Return ONLY the customer's message.

Do NOT include:

Customer:

Name:

Explanation:

Notes:

Reasoning:

Markdown formatting.

Return only the exact message that would appear inside the chat bubble.

"""
    response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
    )

    return response.text.strip()


def process_customer_ai():

    print("\n==============================")
    print("CUSTOMER AI ENGINE STARTED")
    print("==============================")

    try:

        ai_sheet = get_customer_ai_sheet()
        communication_sheet = get_communications_sheet()

        ai_rows = ai_sheet.get_all_records()
        onboarding = get_onboarding_sheet().get_all_records()
        communications = communication_sheet.get_all_records()

        print("AI Customers Found:", len(ai_rows))

        for i, ai in enumerate(ai_rows, start=2):

            if str(ai.get("enabled", "")).strip().lower() != "yes":
                continue

            if str(ai.get("conversation_state", "")).strip().lower() != "open":
                continue

            if str(ai.get("waiting_for", "")).strip().lower() != "ai":
                continue

            customer = next(
                (
                    c for c in onboarding
                    if str(c.get("customer_id", "")) == str(ai.get("customer_id", ""))
                ),
                None
            )

            if not customer:
                print("Customer not found:", ai.get("customer_id"))
                continue

            history = [
                m for m in communications
                if str(m.get("customer_id", "")) == str(ai.get("customer_id", ""))
            ]

            if len(history) > 0:
                last_sender = str(history[-1].get("sender", "")).strip().lower()

                if last_sender == "customer":
                    print("Waiting for agent reply:", customer.get("company_name"))
                    ai["waiting_for"] = "Agent"

                    ai_sheet.update(
                        f"A{i}:M{i}",
                        [[
                            ai.get("customer_id", ""),
                            ai.get("enabled", ""),
                            ai.get("personality", ""),
                            ai.get("customer_role", ""),
                            ai.get("goal", ""),
                            ai.get("conversation_state", ""),
                            ai.get("waiting_for", ""),
                            ai.get("message_count", ""),
                            ai.get("last_ai_reply", ""),
                            ai.get("next_reply_after", ""),
                            ai.get("reply_probability", ""),
                            ai.get("max_messages", ""),
                            ai.get("memory_summary", "")
                        ]]
                    )

                    continue

            message = generate_customer_reply(
                customer,
                ai,
                history
            )

            conversation_id = (
                history[-1].get("conversation_id", "")
                if len(history) > 0
                else f"CONV-{customer.get('customer_id', '')}"
            )

            message_id = f"MSG-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            communication_sheet.append_row([

                conversation_id,
                message_id,
                customer.get("customer_id", ""),
                customer.get("lead_id", ""),
                customer.get("company_name", ""),
                customer.get("contact_person", ""),
                customer.get("email", ""),
                customer.get("phone", ""),
                "Customer",
                "Chat",
                "General Inquiry",
                message.strip(),
                "",
                "Open",
                "Medium",
                customer.get("assigned_to", ""),
                "AI",
                now,
                "Unread",
                "",
                "Yes",
                customer.get("payment_stage", ""),
                "Completed"

            ])

            current_count = ai.get("message_count", "")

            try:
                current_count = int(current_count)
            except:
                current_count = 0

            ai["waiting_for"] = "Agent"
            ai["last_ai_reply"] = now
            ai["message_count"] = str(current_count + 1)
            ai["next_reply_after"] = ""

            ai_sheet.update(
                f"A{i}:M{i}",
                [[
                    ai.get("customer_id", ""),
                    ai.get("enabled", ""),
                    ai.get("personality", ""),
                    ai.get("customer_role", ""),
                    ai.get("goal", ""),
                    ai.get("conversation_state", ""),
                    ai.get("waiting_for", ""),
                    ai.get("message_count", ""),
                    ai.get("last_ai_reply", ""),
                    ai.get("next_reply_after", ""),
                    ai.get("reply_probability", ""),
                    ai.get("max_messages", ""),
                    ai.get("memory_summary", "")
                ]]
            )

            print("✅ AI message saved:", customer.get("company_name"))

        print("==============================")
        print("CUSTOMER AI ENGINE FINISHED")
        print("==============================")

    except Exception as e:

        print("CUSTOMER AI ERROR:", str(e))


# def initialize(ai_sheet_func,
#                onboarding_func,
#                communication_func):

#     global get_customer_ai_sheet_func
#     global get_onboarding_sheet
#     global get_communications_sheet

#     get_customer_ai_sheet_func = ai_sheet_func
#     get_onboarding_sheet = onboarding_func
#     get_communications_sheet = communication_func