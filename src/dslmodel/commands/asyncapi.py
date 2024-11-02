import typer
import yaml
from pathlib import Path
from jinja2 import Template
from loguru import logger

from dslmodel.template import render
from dslmodel.utils.str_tools import dasherize, pythonic_str

app = typer.Typer()

# Initialize logger
logger.add("debug.log", rotation="1 MB")

# Templates for handler and Vue page files
handler_template = """from pydantic import BaseModel
from loguru import logger


# Define Pydantic model for validation
class {{ operation_name  | camelize }}Payload(BaseModel):
{% for field, type in fields.items() %}
    {{ field }}: {{ type }}
{% endfor %}


# Event handler function
async def handle_event(sid: str, data: {{ operation_name  | camelize }}Payload, sio):
    logger.info(f"Handling {{ operation_name }} for SID '{sid}' with data: {{ '{' }}data.model_dump(){{ '}' }}")

    # Add your logic here, such as updating database records, etc.
    # Emit a success acknowledgment back to the client
    await sio.emit("{{ operation_name }}_ack", 
                   {"status": "success", 
                    "message": "{{ operation_name }} handled successfully"}, 
                   room=sid)
    
"""

page_template = """
<template>
  <div>
    <button @click="handle{{ operation_name | camelize }}">Send {{ operation_name | camelize }}</button>
    <div v-if="receivedData">Callback Data: {{ receivedData }}</div>
    <div v-if="observedData">Observable Data: {{ observedData }}</div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue';
import { useOperation } from '@/composables/useOperation';

const { send{{ operation_name | camelize }}, receive{{ operation_name | camelize }}, observe{{ operation_name | camelize }} } = useOperation('{{ operation_name }}');

const receivedData = ref(null);
const observedData = ref(null);

// Callback-based receive example
const unsubscribeCallback = receive{{ operation_name | camelize }}((data) => {
  receivedData.value = data;
  console.log('Received data (callback):', data);
});

// Observable-based receive example
const { observable, unsubscribe: unsubscribeObservable } = observe{{ operation_name | camelize }}();
const subscription = observable.subscribe((data) => {
  observedData.value = data;
  console.log('Received data (observable):', data);
});

// Send data to server
const handle{{ operation_name | camelize }} = async () => {
  try {
    const response = await send{{ operation_name | camelize }}({
      {% for field in fields %}
      {{ field }}: '{{ field | default }}'{{ ',' if not loop.last }}
      {% endfor %}
    });
    console.log('Server acknowledgment:', response);
  } catch (error) {
    console.error('Error:', error);
  }
};

// Cleanup on component unmount
onUnmounted(() => {
  unsubscribeCallback();
  unsubscribeObservable();
  subscription.unsubscribe();
});
</script>
"""


def load_asyncapi_file(asyncapi_file: Path) -> dict:
    """Load and parse the AsyncAPI YAML file."""
    logger.info(f"Loading AsyncAPI file from '{asyncapi_file}'")
    try:
        with open(asyncapi_file, 'r') as f:
            asyncapi_data = yaml.safe_load(f)
        logger.debug(f"AsyncAPI data loaded successfully: {asyncapi_data}")
        return asyncapi_data
    except Exception as e:
        logger.error(f"Failed to load AsyncAPI file: {e}")
        raise typer.Exit(code=1)


def extract_operation_fields(message: dict) -> dict:
    """Extract fields from a message schema in AsyncAPI file."""
    logger.debug(f"Extracting fields from message: {message}")
    fields = {}
    payload = message.get("payload", {}).get("properties", {})
    for field_name, field_info in payload.items():
        fields[field_name] = convert_to_pydantic_type(field_info["type"])
    logger.debug(f"Extracted fields: {fields}")
    return fields


def render_template(template: str, context: dict) -> str:
    """Render a Jinja template with the provided context."""
    logger.debug(f"Rendering template with context: {context}")
    return render(template, **context)


def write_to_file(output_path: Path, content: str):
    """Write content to a specified file path."""
    logger.info(f"Writing file to '{output_path}'")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(content)
    logger.debug(f"File written successfully to '{output_path}'")


def convert_to_pydantic_type(field_type: str) -> str:
    """Convert AsyncAPI types to Pydantic types."""
    type_mappings = {
        "string": "str",
        "integer": "int",
        "number": "float",
        "boolean": "bool",
        "array": "List",
        "object": "Dict",
    }
    pydantic_type = type_mappings.get(field_type, "Any")
    logger.debug(f"Converted AsyncAPI type '{field_type}' to Pydantic type '{pydantic_type}'")
    return pydantic_type


@app.command("handlers")
def export_handlers(asyncapi_file: Path = typer.Option("asyncapi.yaml",
                                                       help="Path to the AsyncAPI YAML file"),
                    output_dir: Path = typer.Option("/Users/sac/dev/dslmodel/src/dslmodel/mq7/events",
                                                    help="Output directory for event handlers")):
    """
    Export Python handler files based on the AsyncAPI YAML specification.
    """
    asyncapi_data = load_asyncapi_file(asyncapi_file)

    # Process each operation in the AsyncAPI specification
    for operation_name, operation_info in asyncapi_data.get("operations", {}).items():
        # Retrieve the channel reference and channel information
        channel_ref = operation_info.get("channel", {}).get("$ref")
        if not channel_ref:
            logger.warning(f"No channel reference found for operation '{operation_name}'")
            continue

        channel_name = channel_ref.split('/')[-1]
        logger.info(f"Processing operation '{operation_name}' on channel '{channel_name}'")

        # Load the channel information and get the message structure
        channel_info = asyncapi_data.get("channels", {}).get(channel_name)
        if not channel_info:
            logger.warning(f"Channel '{channel_name}' not found in AsyncAPI data.")
            continue

        # Extract fields from the first message in the channel
        message = list(channel_info.get("messages", {}).values())[0]
        fields = extract_operation_fields(message)

        # Prepare the context for rendering the handler file
        handler_content = render_template(handler_template, {
            "model_name": operation_name.capitalize() + "Data",
            "fields": fields,
            "operation_name": operation_name,
        })

        # Define the output path and write the handler file
        output_path = output_dir / f"{pythonic_str(operation_name)}.py"
        write_to_file(output_path, handler_content)


@app.command("pages")
def export_pages(asyncapi_file: Path = typer.Option("asyncapi.yaml",
                                                    help="Path to the AsyncAPI YAML file"),
                 output_dir: Path = typer.Option("/Users/sac/dev/dslmodel/nuxtbe/app/pages",
                                                 help="Path to the output directory for Vue pages")):
    """
    Export Vue pages based on the AsyncAPI YAML specification.
    """
    asyncapi_data = load_asyncapi_file(asyncapi_file)

    for operation_name, operation_info in asyncapi_data.get("operations", {}).items():
        channel_ref = operation_info.get("channel", {}).get("$ref")
        if not channel_ref:
            logger.warning(f"No channel reference found for operation '{operation_name}'")
            continue

        channel_name = channel_ref.split('/')[-1]
        logger.info(f"Processing operation '{operation_name}' on channel '{channel_name}'")

        channel_info = asyncapi_data.get("channels", {}).get(channel_name)
        if not channel_info:
            logger.warning(f"Channel '{channel_name}' not found in AsyncAPI data.")
            continue

        # Extract fields from the first message in the channel
        message = list(channel_info.get("messages", {}).values())[0]
        fields = extract_operation_fields(message)

        page_content = render_template(page_template, {
            "operation_name": operation_name,
            "fields": fields.keys(),
        })

        output_path = output_dir / f"{dasherize(operation_name)}.vue"
        write_to_file(output_path, page_content)


if __name__ == "__main__":
    app()
