import os
import threading
import queue
import tkinter as tk
from tkinter import ttk
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent


@tool
def calculator(expression: str) -> str:
    """Evaluate a math expression and return the result."""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"


def create_agent():
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables.")
    model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)
    return create_react_agent(model, tools=[calculator])


class ChatGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Hunter – Desktop Chat")

        self.agent = create_agent()
        self.msg_queue: "queue.Queue[str]" = queue.Queue()
        self.worker: threading.Thread | None = None

        self._build_ui()
        self._poll_queue()

    def _build_ui(self) -> None:
        self.root.geometry("780x560")
        self.root.minsize(640, 420)

        container = ttk.Frame(self.root, padding=10)
        container.pack(fill=tk.BOTH, expand=True)

        self.chat = tk.Text(
            container,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg="white",
            fg="#111111",
        )
        self.chat.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        # Simple theming for roles (high-contrast on white bg)
        self.chat.tag_config("user", foreground="#0b5fff")
        self.chat.tag_config("assistant", foreground="#111111")
        self.chat.tag_config("system", foreground="#555555", font=(None, 9, "italic"))

        bottom = ttk.Frame(container)
        bottom.pack(fill=tk.X, side=tk.BOTTOM, pady=(8, 0))

        self.entry = ttk.Entry(bottom)
        self.entry.pack(fill=tk.X, side=tk.LEFT, expand=True)
        self.entry.bind("<Return>", self._on_send)

        self.send_btn = ttk.Button(bottom, text="Send", command=self._on_send)
        self.send_btn.pack(side=tk.LEFT, padx=(8, 0))

        self._append_line("Type a message and press Enter.", tag="system")

    def _append(self, text: str, tag: str | None = None) -> None:
        self.chat.configure(state=tk.NORMAL)
        if tag:
            self.chat.insert(tk.END, text, tag)
        else:
            self.chat.insert(tk.END, text)
        self.chat.see(tk.END)
        self.chat.configure(state=tk.DISABLED)

    def _append_line(self, text: str, tag: str | None = None) -> None:
        self._append(text + "\n", tag)

    def _on_send(self, event=None) -> None:
        message = self.entry.get().strip()
        if not message or self.worker and self.worker.is_alive():
            return
        self.entry.delete(0, tk.END)
        self._append_line(f"You: {message}", tag="user")
        self._append("Assistant: ", tag="assistant")

        # Start background worker
        self.send_btn.configure(state=tk.DISABLED)
        self.worker = threading.Thread(target=self._run_agent_stream, args=(message,), daemon=True)
        self.worker.start()

    def _run_agent_stream(self, user_input: str) -> None:
        try:
            for chunk in self.agent.stream({"messages": [HumanMessage(content=user_input)]}):
                if "agent" in chunk and "messages" in chunk["agent"]:
                    for message in chunk["agent"]["messages"]:
                        self.msg_queue.put(message.content)
                if "output" in chunk:
                    self.msg_queue.put(chunk["output"])
        except Exception as e:
            self.msg_queue.put(f"\n[Error] {e}\n")
        finally:
            self.msg_queue.put("__END__")

    def _poll_queue(self) -> None:
        try:
            while True:
                item = self.msg_queue.get_nowait()
                if item == "__END__":
                    self._append("\n")
                    self.send_btn.configure(state=tk.NORMAL)
                else:
                    self._append(item, tag="assistant")
        except queue.Empty:
            pass
        # Schedule next poll
        self.root.after(30, self._poll_queue)


def main() -> None:
    root = tk.Tk()
    # Improve default ttk look
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    app = ChatGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()


