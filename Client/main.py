from modules.client import Client
from modules.screen_manager import ScreenManager

def main():
    client = Client()
    ScreenManager(client)

if __name__ == "__main__":
    main()