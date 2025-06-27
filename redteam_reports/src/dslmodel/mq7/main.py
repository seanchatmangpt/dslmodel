from dslmodel.mq7.event_registry import register_events
from dslmodel.mq7.mq7_v1 import socket_app


def main():
    register_events()

    import uvicorn
    uvicorn.run(socket_app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
