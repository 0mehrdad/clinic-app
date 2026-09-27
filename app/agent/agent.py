import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from app.agent.tools import (
    get_services_tool,
    get_doctors_tool,
    check_availability_tool,
    book_appointment_tool,
    reschedule_appointment_tool,
    cancel_appointment_tool,
    find_patient_tool,
    register_patient_tool,
)

load_dotenv()


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)
TOOL_FUNCTIONS = {
    "get_services": get_services_tool,
    "get_doctors": get_doctors_tool,
    "check_availability": check_availability_tool,
    "book_appointment": book_appointment_tool,
    "reschedule_appointment": reschedule_appointment_tool,
    "cancel_appointment": cancel_appointment_tool,
    "find_patient": find_patient_tool,
    "register_patient": register_patient_tool,
}

TOOLS = [
    {
    "type": "function",
    "function": {
        "name": "reschedule_appointment",
        "description": (
            "Reschedule an existing appointment after the user has "
            "explicitly confirmed the new date and time."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "appointment_id": {
                    "type": "integer"
                },
                "new_start_time": {
                    "type": "string",
                    "description": (
                        "New appointment start time in ISO format, "
                        "for example 2026-09-28T11:00:00."
                    )
                }
            },
            "required": [
                "appointment_id",
                "new_start_time"
            ]
        }
    }
},
{
    "type": "function",
    "function": {
        "name": "register_patient",
        "description": (
            "Register a new patient and link their Telegram chat ID."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "phone": {"type": "string"},
                "email": {"type": "string"},
                "telegram_chat_id": {"type": "string"},
            },
            "required": [
                "name",
                "phone",
                "email",
                "telegram_chat_id",
            ],
        },
    },
},
{
    "type": "function",
    "function": {
        "name": "find_patient",
        "description": (
            "Find an existing patient using their phone number, "
            "email address, or Telegram chat ID."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "identity_type": {
                    "type": "string",
                    "enum": ["phone", "email", "telegram"],
                },
                "identity_value": {
                    "type": "string",
                },
            },
            "required": [
                "identity_type",
                "identity_value",
            ],
        },
    },
},
{
    "type": "function",
    "function": {
        "name": "cancel_appointment",
        "description": (
            "Cancel an existing appointment after the user has "
            "explicitly confirmed they want to cancel it."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "appointment_id": {
                    "type": "integer"
                }
            },
            "required": ["appointment_id"]
        }
    }
},
    {
    "type": "function",
    "function": {
        "name": "book_appointment",
        "description": (
            "Book an appointment after the user has explicitly confirmed "
            "the doctor, service, date and time."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "patient_id": {
                    "type": "integer"
                },
                "doctor_id": {
                    "type": "integer"
                },
                "service_id": {
                    "type": "integer"
                },
                "start_time": {
                    "type": "string",
                    "description": (
                        "Appointment start time in ISO format, "
                        "for example 2026-09-28T10:00:00."
                    )
                }
            },
            "required": [
                "patient_id",
                "doctor_id",
                "service_id",
                "start_time"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_services",
            "description": (
                "Get all services offered by the women's clinic, "
                "including prices and durations."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_doctors",
            "description": (
                "Get the doctors who provide a specific clinic service."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "service_id": {
                        "type": "integer",
                        "description": "The ID of the clinic service.",
                    }
                },
                "required": ["service_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": (
                "Check available appointment times for a doctor "
                "and service on a specific date."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "doctor_id": {
                        "type": "integer",
                    },
                    "service_id": {
                        "type": "integer",
                    },
                    "appointment_date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format.",
                    },
                },
                "required": [
                    "doctor_id",
                    "service_id",
                    "appointment_date",
                ],
            },
        },
    },
]

def chat(message: str, messages: list):
    messages.append(
        {
            "role": "user",
            "content": message,
        }
    )

    while True:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        assistant_message = response.choices[0].message

        # No tool requested = we have the final answer.
        if not assistant_message.tool_calls:
            return assistant_message.content

        messages.append(assistant_message)

        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(
                tool_call.function.arguments
            )

            tool_function = TOOL_FUNCTIONS.get(tool_name)

            if tool_function is None:
                result = {
                    "success": False,
                    "message": f"Unknown tool: {tool_name}",
                }
            else:
                result = tool_function(**arguments)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(
                        result,
                        default=str,
                    ),
                }
            )