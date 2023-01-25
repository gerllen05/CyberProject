from modules.client import Client
from modules.screen_manager import ScreenManager

def main():
    client = Client()
    ScreenManager(client)
    client.start()


if __name__ == "__main__":
    main()