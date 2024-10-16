# # test_assistant.py
#
# import hashlib
# import json
# from typing import Any
#
# from dslmodel.mixins.tool_mixin import Assistant
#
#
# class MockOpenAI:
#     def __init__(self):
#         self.preloaded_responses: dict[str, Any] = {}
#
#     def preload_response(self, request_signature: str, response: Any):
#         self.preloaded_responses[request_signature] = response
#
#     def create(
#         self,
#         model: str,
#         messages: list[dict[str, Any]],
#         tools: list[dict[str, Any]] | None = None,
#         **kwargs,
#     ) -> Any:
#         request_signature = self._generate_request_signature(model, messages, tools, kwargs)
#         response = self.preloaded_responses.get(request_signature)
#         if response is None:
#             raise ValueError("No preloaded response for the given request.")
#         return response
#
#     def _generate_request_signature(
#         self,
#         model: str,
#         messages: list[dict[str, Any]],
#         tools: list[dict[str, Any]] | None,
#         kwargs: dict[str, Any],
#     ) -> str:
#         request_content = {"model": model, "messages": messages, "tools": tools, **kwargs}
#         request_json = json.dumps(request_content, sort_keys=True)
#         signature = hashlib.sha256(request_json.encode("utf-8")).hexdigest()
#         return signature
#
#
# def test_assistant_get_delivery_date_with_toolmixin():
#     """
#     Test the assistant's ability to retrieve the delivery date for an order using ToolMixin.
#     """
#     # Create an instance of the assistant
#     assistant = Assistant()
#
#     # Create an instance of the MockOpenAI class
#     mock_openai = MockOpenAI()
#
#     # ----------------------------
#     # Step 1: User asks for delivery date
#     # ----------------------------
#
#     # Define the messages for the first API call
#     messages_step1 = [
#         {
#             "role": "system",
#             "content": "You are a helpful customer support assistant. Use the supplied tools to assist the user.",
#         },
#         {"role": "user", "content": "Hi, can you tell me the delivery date for my order?"},
#     ]
#
#     # Get the tool definitions from the assistant
#     tools = assistant.get_tool_definitions()
#
#     # Preload the expected response from the API
#     response_step1 = {
#         "choices": [
#             {
#                 "message": {
#                     "role": "assistant",
#                     "content": "Sure! Could you please provide your order ID?",
#                 },
#                 "finish_reason": "stop",
#             }
#         ]
#     }
#
#     # Generate the request signature for the first API call
#     request_signature_step1 = mock_openai._generate_request_signature(
#         model="gpt-4o", messages=messages_step1, tools=tools, kwargs={}
#     )
#
#     # Preload the response into the mock API
#     mock_openai.preload_response(request_signature_step1, response_step1)
#
#     # ----------------------------
#     # Step 2: User provides the order ID
#     # ----------------------------
#
#     # Define the messages for the second API call
#     messages_step2 = messages_step1 + [
#         {"role": "assistant", "content": "Sure! Could you please provide your order ID?"},
#         {"role": "user", "content": "It's order_12345"},
#     ]
#
#     # Preload the expected response from the API
#     response_step2 = {
#         "choices": [
#             {
#                 "message": {
#                     "role": "assistant",
#                     "tool_calls": [
#                         {
#                             "id": "call_001",
#                             "type": "function",
#                             "function": {
#                                 "name": "get_delivery_date",
#                                 "arguments": json.dumps({"order_id": "order_12345"}),
#                             },
#                         }
#                     ],
#                 },
#                 "finish_reason": "tool_calls",
#             }
#         ]
#     }
#
#     # Generate the request signature for the second API call
#     request_signature_step2 = mock_openai._generate_request_signature(
#         model="gpt-4o", messages=messages_step2, tools=tools, kwargs={}
#     )
#
#     # Preload the response into the mock API
#     mock_openai.preload_response(request_signature_step2, response_step2)
#
#     # ----------------------------
#     # Step 3: Assistant processes the function call result
#     # ----------------------------
#
#     # Process the tool call using the assistant's method
#     tool_call = response_step2["choices"][0]["message"]["tool_calls"][0]
#     function_result_message = assistant.process_tool_call(tool_call)
#
#     # Define the messages for the third API call
#     messages_step3 = messages_step2 + [
#         response_step2["choices"][0]["message"],
#         function_result_message,
#     ]
#
#     # Preload the expected response from the API
#     response_step3 = {
#         "choices": [
#             {
#                 "message": {
#                     "role": "assistant",
#                     "content": "Your order #order_12345 is scheduled for delivery on 2024-10-15.",
#                 },
#                 "finish_reason": "stop",
#             }
#         ]
#     }
#
#     # Generate the request signature for the third API call
#     request_signature_step3 = mock_openai._generate_request_signature(
#         model="gpt-4o", messages=messages_step3, tools=None, kwargs={}
#     )
#
#     # Preload the response into the mock API
#     mock_openai.preload_response(request_signature_step3, response_step3)
#
#     # ----------------------------
#     # Simulate the conversation using the mock API
#     # ----------------------------
#
#     # First API call
#     response1 = mock_openai.create(model="gpt-4o", messages=messages_step1, tools=tools)
#     assistant_message1 = response1["choices"][0]["message"]["content"]
#     print(f"Assistant: {assistant_message1}")
#     assert assistant_message1 == "Sure! Could you please provide your order ID?"
#
#     # Second API call
#     response2 = mock_openai.create(model="gpt-4o", messages=messages_step2, tools=tools)
#     assistant_message2 = response2["choices"][0]["message"]
#
#     # Ensure the assistant is making a tool call
#     assert "tool_calls" in assistant_message2
#
#     # Process the tool call
#     tool_call = assistant_message2["tool_calls"][0]
#     function_result_message = assistant.process_tool_call(tool_call)
#
#     # Third API call
#     response3 = mock_openai.create(model="gpt-4o", messages=messages_step3)
#     assistant_message3 = response3["choices"][0]["message"]["content"]
#     print(f"Assistant: {assistant_message3}")
#     expected_message = "Your order #order_12345 is scheduled for delivery on 2024-10-15."
#     assert assistant_message3 == expected_message
#
#     # ----------------------------
#     # Conclusion
#     # ----------------------------
#
#     print("Test passed: The assistant correctly retrieved the delivery date using ToolMixin.")
