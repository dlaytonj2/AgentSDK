
from openai import OpenAI
import time
import base64
import os
from dotenv import load_dotenv


import json
import base64
from urllib.parse import urlparse


load_dotenv()
OpenAI.api_key = os.getenv("OPENAI_API_KEY")


client = OpenAI()


#Computer 
from typing import Protocol, List, Literal, Dict


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
    "windows": "Meta"
}

# Define a BasePlayWright Coumputer 

class BasePlaywrightComputer:
    """
    Abstract base for Playwright-based computers:

      - Subclasses override `_get_browser_and_page()` to do local or remote connection,
        returning (Browser, Page).
      - This base class handles context creation (`__enter__`/`__exit__`),
        plus standard "Computer" actions like click, scroll, etc.
      - We also have extra browser actions: `goto(url)` and `back()`.
    """

    environment: Literal["browser"] = "browser" #other values "mac", "windows", "ubuntu"
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

    def wait(self) -> None:
        time.sleep(1)

    def move(self, x: int, y: int) -> None:
        self._page.mouse.move(x, y)

    def keypress(self, keys: List[str]) -> None:
        # for keypress we need to map the CUA key to Playwright key notation 
        mapped_keys = [CUA_KEY_TO_PLAYWRIGHT_KEY.get(key.lower(), key) for key in keys]
        # Allow for single and combination key presses
        # press down in each key in sequence
        for key in mapped_keys:
            self._page.keyboard.down(key)
        # release each key in reversed order
        for key in reversed(mapped_keys):
            self._page.keyboard.up(key)

    def drag(self, path: List[Dict[str, int]]) -> None:
        print('\n Drag method:', path)

        if not path:
            return
        self._page.mouse.move(path[0]["x"], path[0]["y"])
        self._page.mouse.down()
        for point in path[1:]:
            self._page.mouse.move(point["x"], point["y"])
        self._page.mouse.up()

    def drag(self, path: list[tuple[int, int]]) -> None:
        if not path:
            return
        # move cursor to first co-ordinate
        # press and hold the mouse button down 
        self.page.mouse.move(path[0][0], path[0][1])
        self.page.mouse.down()
        # iterate through the remaining coordinates on the path
        # skipping the first one because we are already there 
        for px, py in path[1:]:
            self.page.mouse.move(px, py)
        # release the mouse
        self.page.mouse.up()

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
            chromium_sandbox=False,
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
        print("\n New page opened.")
        self._page = page
        page.on("close", self._handle_page_close)
        
    def _handle_page_close(self, page: Page):
        """Handle the closure of a page."""
        print("Page closed. ")
        if self._page == page:
            if self._browser.contexts[0].pages:
                self._page = self._browser.contexts[0].pages[-1]
            else:
                print("Warning: All pages have been closed.")
                self._page = None



def take_action(action, action_type, call_id, computer: LocalPlaywrightComputer):
    """Handle each item; may cause a computer action + screenshot."""


    if action_type == 'screenshot':
        computer.screenshot()
        print(f"\n Type = Computer Call: {action_type} ()")
    
    else: 
        action_args = vars(action)

        # print("\n Inside take_action Action args:",action_args])

        if 'type' in action_args:
            del action_args['type']

        print(f"\n Type = Computer Call: {action_type} ({action_args})")

        getattr(computer, action_type)(**action_args)
      

    screenshot_base64 = computer.screenshot()

    computer_url = None 
    if computer.environment == "browser":
        current_url = computer.get_current_url() 

    call_output = create_call_output(call_id, screenshot_base64,current_url)
    # print('\n call output ... ', call_output["type"],call_output["call_id"], call_output["output"]["type"])
    return [call_output]

def create_call_output(call_id,screenshot_base64, current_url):
    ''' After the computer action has been taken build the call output '''
    
    pending_checks =[]
   
    call_output = {
            "type": "computer_call_output",
            "call_id": call_id,
            "acknowledged_safety_checks": pending_checks,
            "output": {
                "type": "input_image",
                "image_url": f"data:image/png;base64,{screenshot_base64}",
            },
        }
    '''
    Where possible, it is highly recommended to pass in the optional parameter current_url as part of the computer_call_output,
    as it can help increase the accuracy of our safety checks.
    '''
    if current_url is not None:
        call_output["output"]["current_url"] = current_url
        
    # print(f'\n Call output created: current url is {current_url}')
    return (call_output)

    
# Main function to run the loop is here 

def main():
    """
    Run the CUA (Computer Use Assistant) loop, using Local Playwright.
    Maintaining my own response history, so it can be printed when finished 
    Added an exit from the chat when a Message is received -- without this the loop just carried on after its goal had been reached
    Add an exit from the loop if the user enters quit 
    """
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
        # maintaining my own response history 
        response_history = []
        first_time=True

        while True:  # get user input until user enters "quit"
            
            if first_time: 
                user_input = input("\n Working ... What would you like to browse today? If you are finished, just type quit >  ")
            else:
                user_input = input("\n I have retained the history of this chat. How would you like to proceed? If you are finished, just type quit >  ")
            first_time=False

            # Check if user wants to quit the program
            if user_input.lower() == 'quit':
                print("\n Exiting the program... Goodbye!")
                break
            
            response_history.append({"role": "user", "content": user_input})
            
            while True:  # keep looping until we get a final response
                
                response = client.responses.create(
                    model="computer-use-preview",
                    input=response_history,
                    tools=tools,
                    truncation="auto",
                    reasoning={"generate_summary": "concise" }
                    
                )

                         
                if response.output[0].type == 'reasoning':
                    print(f'\n Type = Reasoning: reasoning effort = {response.reasoning.effort}')
                 
                if response.output[0].type == 'message':
                    print(f'\n Type = Message: \n {response.output_text}')
                    print('\n  Pausing ... \n  Respond to message or enter new prompt >')
                    break
                
                #add the response to the response history
                response_dict = response.to_dict()
                response_history += response_dict["output"]


                ctr = 0

                for item in response.output:
                    ctr=ctr+1
                    if item.type == 'computer_call':
                        # add the response to call history from take_action 
                        response_history += take_action(item.action, item.action.type, item.call_id, computer)
        
        
        # Write the response_history list to a file when finished
        try:
            with open('computer_use_response_history.txt', 'w') as file:
                # Convert the response_history list to a formatted string representation
                for i, item in enumerate(response_history):
                    # Set image_url to None to avoid storing large base64 strings
                    if item.get('type') == 'computer_call_output' and 'output' in item:
                        if 'image_url' in item['output']:
                            item['output']['image_url'] = None
                    
                    file.write(f"Item {i}:\n")
                    file.write(json.dumps(item, indent=4))
                    file.write("\n\n")
            print(f"\n You can find the history of responses in: computer_use_response_history.txt")
        
        except Exception as e:
            print(f"\nError writing to file: {e}")
                    

if __name__ == "__main__":
    main()