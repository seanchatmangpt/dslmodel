# # test_openapi_tool_mixin.py
#
# import pytest
# from fastapi.testclient import TestClient
# from fastapi import FastAPI
# from .example_api import ExampleAPI, AddParticipantInput, ParticipantOutput, CreateMeetingInput, MeetingOutput
#
# # Initialize FastAPI app with ExampleAPI
# app = FastAPI()
#
# @app.on_event("startup")
# async def startup_event():
#     example_api = ExampleAPI()
#     example_api.register_routes(app)
#
# client = TestClient(app)
#
# @pytest.mark.asyncio
# def test_openapi_schema():
#     # Fetch the OpenAPI schema
#     response = client.get("/openapi.json")
#     assert response.status_code == 200, "Failed to fetch OpenAPI schema."
#
#     # Parse the OpenAPI schema
#     openapi_schema = response.json()
#     assert "paths" in openapi_schema, "OpenAPI schema missing 'paths'."
#
#     # Check for tool endpoints in paths
#     assert "/add_participant" in openapi_schema["paths"], "Expected '/add_participant' path not found."
#     assert "/create_meeting" in openapi_schema["paths"], "Expected '/create_meeting' path not found."
#
#     # Check components
#     assert "components" in openapi_schema, "OpenAPI schema missing 'components'."
#
#     # Check that models are present in the schema
#     schemas = openapi_schema["components"]["schemas"]
#     assert "AddParticipantInput" in schemas, "AddParticipantInput schema not found in OpenAPI."
#     assert "ParticipantOutput" in schemas, "ParticipantOutput schema not found in OpenAPI."
#     assert "CreateMeetingInput" in schemas, "CreateMeetingInput schema not found in OpenAPI."
#     assert "MeetingOutput" in schemas, "MeetingOutput schema not found in OpenAPI."
#
#     # Check the properties for AddParticipantInput schema
#     add_participant_input = schemas["AddParticipantInput"]
#     assert "properties" in add_participant_input, "AddParticipantInput schema missing 'properties'."
#     assert "name" in add_participant_input["properties"], "AddParticipantInput missing 'name' property."
#     assert "role" in add_participant_input["properties"], "AddParticipantInput missing 'role' property."
#
#     # Check the properties for ParticipantOutput schema
#     participant_output = schemas["ParticipantOutput"]
#     assert "properties" in participant_output, "ParticipantOutput schema missing 'properties'."
#     assert "name" in participant_output["properties"], "ParticipantOutput missing 'name' property."
#     assert "role" in participant_output["properties"], "ParticipantOutput missing 'role' property."
#
#     # Check the properties for CreateMeetingInput schema
#     create_meeting_input = schemas["CreateMeetingInput"]
#     assert "properties" in create_meeting_input, "CreateMeetingInput schema missing 'properties'."
#     assert "name" in create_meeting_input["properties"], "CreateMeetingInput missing 'name' property."
#     assert "participants" in create_meeting_input["properties"], "CreateMeetingInput missing 'participants' property."
#
#     # Check the properties for MeetingOutput schema
#     meeting_output = schemas["MeetingOutput"]
#     assert "properties" in meeting_output, "MeetingOutput schema missing 'properties'."
#     assert "name" in meeting_output["properties"], "MeetingOutput missing 'name' property."
#     assert "participants" in meeting_output["properties"], "MeetingOutput missing 'participants' property."
