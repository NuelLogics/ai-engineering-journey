from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import openai
from pydantic import BaseModel, ConfigDict
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Create a logger for the current module
logger = logging.getLogger(__name__)


load_dotenv()

try:
    client = OpenAI(
        api_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
    )
except openai.OpenAIError as e:
    logger.error(
        "OpenAI client setup failed. Check the API key and parameters: %s",
        e,
    )
    # -------Commented out code to list all available models in the Groq API. Uncomment to use.-------
# models = client.models.list()

# for model in models.data:
#     print(model.id)
# ----------------------------------------------------------------


def chat_safe(system_prompt, user_message, temperature=0.7, max_tokens=500):
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        finish = response.choices[0].finish_reason
        if finish == "length":
            logger.warning(
                f"⚠️  Response cut off — raise max_tokens (used {response.usage.completion_tokens})"
            )

        # logger.info(
        #     f"[chat] tokens: {response.usage.prompt_tokens}in "
        #     f"+ {response.usage.completion_tokens}out "
        #     f"= {response.usage.total_tokens}total"
        # )

        return response.choices[0].message.content

    except openai.BadRequestError as e:
        logger.error("Bad request error. Check your input parameters.")
        logger.error(f"❌ Bad request error - {e}")
    except openai.RateLimitError as e:
        logger.warning("Rate limit hit, slow down or upgrade plan.")
        logger.error(f"❌ Rate limit hit, slow down or upgrade plan - {e}")
    except openai.AuthenticationError as e:
        logger.error("Authentication failed.")
        logger.error(f"❌ Bad API key - {e}")
    except openai.APIConnectionError:
        logger.error("❌ No connection — check your internet")
    except Exception as e:
        logger.error(f"❌ Unexpected error — {e}")

    return None  # always return something, never crash


chat_response = chat_safe(
    system_prompt="You are a concise assistant.",
    user_message="what is the capital of Nigeia?",
)


print(chat_response)


# ------------------ Structured output example with Pydantic ------------------


# class MovieReview(BaseModel):
#     model_config = ConfigDict(extra="forbid")  # Forbids extra fields in the response
#     title: str
#     genre: str
#     rating: int  #
#     summary: str
#     worth_watching: bool


# response2 = client.chat.completions.create(
#     model="openai/gpt-oss-120b",
#     messages=[
#         {"role": "system", "content": "You are a movie critic."},
#         {"role": "user", "content": "Review the movie Inception."},
#     ],
#     # Instead of forcing generic JSON, we pass the exact Pydantic schema
#     response_format={
#         "type": "json_schema",
#         "json_schema": {
#             "name": "MovieReviewSchema",
#             "strict": True,  # Enforces strict adherence on Groq/Llama models
#             "schema": MovieReview.model_json_schema(),  # Extracts schema automatically
#         },
#     },
#     temperature=0.7,
#     max_tokens=300,
# )

# raw = response2.choices[0].message.content

# # Clean up Pydantic validation: .model_validate_json() replaces json.loads()
# # and handles string-to-object conversion safely in one step.
# review = MovieReview.model_validate_json(raw)

# print("=== Structured output (Chat Completions) ===")
# print("Title:        ", review.title)
# print("Genre:        ", review.genre)
# print("Rating:       ", review.rating, "/ 10")
# print("Worth it:     ", review.worth_watching)
# print("Summary:      ", review.summary)


#  ------------


class JobPosting(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_title: str
    job_summary: str
    job_rating: int
    worth_applying: bool


context = "Job Title: Software Engineer IIDescription: We need a skilled Software Engineer to build and scale core features for our cloud platform. You will write clean code, design microservices, and work with product teams to ship reliable software. Requirements include three plus years of coding experience in Python or Go, strong knowledge of REST APIs, and a bachelor's degree in Computer Science or related practical experience. We offer a competitive salary, health insurance, and remote work options.Applicant & Employee Rating Summary (3.8/5.0 stars): Applicants praise the highly technical, interview-prep style coding challenges and the transparency of the recruiting team during the hiring process. Current engineers love the flexible remote work policy, modern tech stack, and collaborative engineering culture. However, multiple reviewers note that the technical interview takes too many rounds to complete. Others mention that fast-paced project deadlines occasionally lead to a hectic work-life balance and technical debt."
response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {
            "role": "system",
            "content": "You are a job posting reviewer. "
            "Return only a valid JSON object matching the requested schema.",
        },
        {
            "role": "user",
            "content": f" context: {context}\n\n user: Review the job posting for a software engineer.",
        },
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "JobPostingSchema",
            "strict": True,
            "schema": JobPosting.model_json_schema(),
        },
    },
    temperature=0,
    max_tokens=1000,
    reasoning_effort="low",
)

raw = response.choices[0].message.content
data = json.loads(raw)  # parse JSON string → Python dict
review = JobPosting(**data)  # validate dict against your Pydantic model

print("=== Structured output (Chat Completions) ===")
print("Title:        ", review.job_title)
print("Summary:      ", review.job_summary)
print("Rating:       ", review.job_rating, "/ 10")
print("Worth applying:", review.worth_applying)


# ----------- STREAMING EXAMPLE -----------------


print("\n=== Streaming response ===")
stream = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Explain how AI(Like ChatGPT) works behind the scenes in 4 sentences, whenever an ordinary non-technical person asks question like 'Who is the president of United States?'.",
        },
    ],
    temperature=0.7,
    max_tokens=300,
    stream=True,  # ← the only change
)

full_response = ""
for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta is not None:
        print(delta, end="", flush=True)  # print token as it arrives
        full_response += delta

print("\n")
print(f"Full response captured: {len(full_response)} characters")
