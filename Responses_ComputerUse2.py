
from openai import OpenAI
import requests
import time
import base64
import os
from dotenv import load_dotenv


import requests

import json
import base64
from PIL import Image
from io import BytesIO
import io
from urllib.parse import urlparse


load_dotenv()
OpenAI.api_key = os.getenv("OPENAI_API_KEY")

# os.environ["OPENAI_API_KEY"]='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'

client = OpenAI()


#Computer 
from typing import Protocol, List, Literal, Dict

class Computer(Protocol):
    """Defines the 'shape' (methods/properties) our loop expects."""

    @property
    def environment(self) -> Literal["windows", "mac", "linux", "browser"]: ...
    @property
    def dimensions(self) -> tuple[int, int]: ...

    def screenshot(self) -> str: ...

    def click(self, x: int, y: int, button: str = "left") -> None: ...

    def double_click(self, x: int, y: int) -> None: ...

    def scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> None: ...

    def type(self, text: str) -> None: ...

    def wait(self, ms: int = 1000) -> None: ...

    def move(self, x: int, y: int) -> None: ...

    def keypress(self, keys: List[str]) -> None: ...

    def drag(self, path: List[Dict[str, int]]) -> None: ...

    def get_current_url() -> str: ...

#BasePlayWrightComputer


from typing import List, Dict, Literal
from playwright.sync_api import sync_playwright, Browser, Page


# key mapping between CUA and Playwright -- see keypress method in BasePlaywright Computer 

CUA_KEY_TO_PLAYWRIGHT_KEY = {
    "/": "Divide",
    "\\": "Backslash",
    "alt": "Alt",
    "arrowdown": "ArrowDown",
    "arrowleft": "ArrowLeft",
    "arrowright": "ArrowRight",
    "arrowup": "ArrowUp",
    "backspace": "Backspace",
    "capslock": "CapsLock",
    "cmd": "Meta",
    "ctrl": "Control",
    "delete": "Delete",
    "end": "End",
    "enter": "Enter",
    "esc": "Escape",
    "home": "Home",
    "insert": "Insert",
    "option": "Alt",
    "pagedown": "PageDown",
    "pageup": "PageUp",
    "shift": "Shift",
    "space": " ",
    "super": "Meta",
    "tab": "Tab",
    "win": "Meta",
}


class BasePlaywrightComputer:
    """
    Abstract base for Playwright-based computers:

      - Subclasses override `_get_browser_and_page()` to do local or remote connection,
        returning (Browser, Page).
      - This base class handles context creation (`__enter__`/`__exit__`),
        plus standard "Computer" actions like click, scroll, etc.
      - We also have extra browser actions: `goto(url)` and `back()`.
    """

    environment: Literal["browser"] = "browser"
    dimensions = (1024, 768)

    def __init__(self):
        self._playwright = None
        self._browser: Browser | None = None
        self._page: Page | None = None

    def __enter__(self):
        # Start Playwright and call the subclass hook for getting browser/page
        self._playwright = sync_playwright().start()
        self._browser, self._page = self._get_browser_and_page()

        # Set up network interception to flag URLs matching domains in BLOCKED_DOMAINS
        def handle_route(route, request):

            url = request.url

            route.continue_()

        self._page.route("**/*", handle_route)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()

    def get_current_url(self) -> str:
        return self._page.url

    # --- Common "Computer" actions ---
    def screenshot(self) -> str:
        """Capture only the viewport (not full_page)."""
        png_bytes = self._page.screenshot(full_page=False)
        return base64.b64encode(png_bytes).decode("utf-8")

    def click(self, x: int, y: int, button: str = "left") -> None:
        match button:
            case "back":
                self.back()
            case "forward":
                self.forward()
            case "wheel":
                self._page.mouse.wheel(x, y)
            case _:
                button_mapping = {"left": "left", "right": "right"}
                button_type = button_mapping.get(button, "left")
                self._page.mouse.click(x, y, button=button_type)

    def double_click(self, x: int, y: int) -> None:
        self._page.mouse.dblclick(x, y)

    def scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> None:
        self._page.mouse.move(x, y)
        self._page.evaluate(f"window.scrollBy({scroll_x}, {scroll_y})")

    def type(self, text: str) -> None:
        self._page.keyboard.type(text)

    def wait(self, ms: int = 1000) -> None:
        time.sleep(ms / 1000)

    def move(self, x: int, y: int) -> None:
        self._page.mouse.move(x, y)

    def keypress(self, keys: List[str]) -> None:
        mapped_keys = [CUA_KEY_TO_PLAYWRIGHT_KEY.get(key.lower(), key) for key in keys]
        for key in mapped_keys:
            self._page.keyboard.down(key)
        for key in reversed(mapped_keys):
            self._page.keyboard.up(key)

    def drag(self, path: List[Dict[str, int]]) -> None:
        if not path:
            return
        self._page.mouse.move(path[0]["x"], path[0]["y"])
        self._page.mouse.down()
        for point in path[1:]:
            self._page.mouse.move(point["x"], point["y"])
        self._page.mouse.up()

    # --- Extra browser-oriented actions ---
    def goto(self, url: str) -> None:
        try:
            return self._page.goto(url)
        except Exception as e:
            print(f"Error navigating to {url}: {e}")

    def back(self) -> None:
        return self._page.go_back()

    def forward(self) -> None:
        return self._page.go_forward()

    # --- Subclass hook ---
    def _get_browser_and_page(self) -> tuple[Browser, Page]:
        """Subclasses must implement, returning (Browser, Page)."""
        raise NotImplementedError



# LocalPlaywrightComputer inherits from BasePlaywrightComputer 

class LocalPlaywrightComputer(BasePlaywrightComputer):
    """Launches a local Chromium instance using Playwright."""

    def __init__(self, headless: bool = False):
        super().__init__()
        self.headless = headless
        self.start_page = 'https://bing.com'

    def _get_browser_and_page(self) -> tuple[Browser, Page]:
        width, height = self.dimensions
        launch_args = [f"--window-size={width},{height}", "--disable-extensions", "--disable-file-system"]
       
        browser = self._playwright.chromium.launch(
            chromium_sandbox=True,
            headless=self.headless,
            args=launch_args,
            env={"DISPLAY": ":0"}
        )
        
        context = browser.new_context()
        
        # Add event listeners for page creation and closure
        context.on("page", self._handle_new_page)
        
        page = context.new_page()
        page.set_viewport_size({"width": width, "height": height})
        page.on("close", self._handle_page_close)

        page.goto(self.start_page)
        
        return browser, page
        
    def _handle_new_page(self, page: Page):
        """Handle the creation of a new page."""
        print("New page created")
        self._page = page
        page.on("close", self._handle_page_close)
        
    def _handle_page_close(self, page: Page):
        """Handle the closure of a page."""
        print("Page closed")
        if self._page == page:
            if self._browser.contexts[0].pages:
                self._page = self._browser.contexts[0].pages[-1]
            else:
                print("Warning: All pages have been closed.")
                self._page = None

def acknowledge_safety_check_callback(message: str) -> bool:
    response = input(
        f"Safety Check Warning: {message}\nDo you want to acknowledge and proceed? (y/n): "
    ).lower()
    return response.strip() == "y"


def handle_item(item, computer: LocalPlaywrightComputer):
    """Handle each item; may cause a computer action + screenshot."""
    if item["type"] == "message":  # print messages
        print(f'\n Type = Message: {item["content"][0]["text"]}')

    if item["type"] == "computer_call":  # perform computer actions
       
        action = item["action"]
        action_type = action["type"]
        action_args = {k: v for k, v in action.items() if k != "type"}
        
        print(f"\n Type = Computer Call: {action_type}({action_args})")

        # give our computer environment action to perform
        getattr(computer, action_type)(**action_args)

        screenshot_base64 = computer.screenshot()

        pending_checks = item.get("pending_safety_checks", [])
        
        for check in pending_checks:
            if not acknowledge_safety_check_callback(check["message"]):
                raise ValueError(f"Safety check failed: {check['message']}")

        computer_url = None 
        if computer.environment == "browser":
            current_url = computer.get_current_url() 


        call_output = create_call_output(item["call_id"], screenshot_base64, pending_checks, current_url)
        return [call_output]

    return []

def create_call_output(call_id,screenshot_base64, pending_checks, current_url):
    ''' After the computer action has been taken build the call output '''
    
    call_output = {
            "type": "computer_call_output",
            "call_id": call_id,
            "acknowledged_safety_checks": pending_checks,
            "output": {
                "type": "input_image",
                "image_url": f"data:image/png;base64,{screenshot_base64}",
            },
        }

    if current_url is not None:
        call_output["output"]["current_url"] = current_url
        
    print(f'\n Call output created: current url is {current_url}')
    return (call_output)

    
# Main function to run the loop is here 

def main():
    """Run the CUA (Computer Use Assistant) loop, using Local Playwright."""

    # create an instance of LocalPlaywrightComputer and call it computer
    with LocalPlaywrightComputer() as computer:
        
        tools = [
            {
                "type": "computer-preview",
                "display_width": computer.dimensions[0],
                "display_height": computer.dimensions[1],
                "environment": computer.environment,
            }
        ]

        items = []
        while True:  # get user input forever
            user_input = input("\n Working ...  What would you like me to do today? > ")
            items.append({"role": "user", "content": user_input})

            while True:  # keep looping until we get a final response
                
                response = client.responses.create(
                    model="computer-use-preview",
                    input=items,
                    tools=tools,
                    truncation="auto",
                    
                )
                if response.output[0].type == 'computer_call':
                    print (f'\n action:{response.output[0].action}')
                    print ('\n',vars(response.output[0].action))

                    print (f'\n action type: {response.output[0].action.type}')
                    
                

                #Convert the response format to a dictionary 
                response_dict = response.to_dict()

                if "output" not in response_dict:
                    print(response)
                    raise ValueError("No output from model")

                items += response_dict["output"]

                for item in response_dict["output"]:
                
                    items += handle_item(item, computer)
                    

                if items[-1].get("role") == "assistant":
                    break


if __name__ == "__main__":
    main()