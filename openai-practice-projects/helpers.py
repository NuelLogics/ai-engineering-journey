"""

=== SKILL 3C: Reusable helpers ===


def chat(system_prompt, user_message, temperature=0.7, max_tokens=500):

    ---Chat Completions wrapper — universal, works with any provider.---

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )

    finish = response.choices[0].finish_reason
    if finish == "length":
        print(
            f"⚠️  Response cut off — raise max_tokens (used {response.usage.completion_tokens})"
        )

    print(
        f"[chat] tokens: {response.usage.prompt_tokens}in "
        f"+ {response.usage.completion_tokens}out "
        f"= {response.usage.total_tokens}total"
    )

    return response.choices[0].message.content


def respond(instructions, user_input, temperature=0.7, max_tokens=500):

    ---Responses API wrapper — OpenAI recommended for new projects.---

    response = client.responses.create(
        model="llama-3.3-70b-versatile",
        instructions=instructions,
        input=user_input,
        temperature=temperature,
        max_output_tokens=max_tokens,
    )

    if response.status != "completed":
        print(f"⚠️  Unexpected status: {response.status}")

    print(
        f"[respond] tokens: {response.usage.input_tokens}in "
        f"+ {response.usage.output_tokens}out "
        f"= {response.usage.total_tokens}total"
    )

    return response.output_text


 --- Test both helpers ---

print("=== chat() helper ===")
print(chat("You are a concise assistant.", "What is a neural network?"))

print("\n=== respond() helper ===")
print(respond("You are a concise assistant.", "What is a neural network?"))



"""
