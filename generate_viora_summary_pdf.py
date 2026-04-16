from pathlib import Path


PAGE_WIDTH = 612
PAGE_HEIGHT = 792
LEFT_MARGIN = 48
RIGHT_MARGIN = 48
TOP_START = 748
BOTTOM_MARGIN = 40
BODY_FONT = "F1"
HEAD_FONT = "F2"
BODY_SIZE = 10
SECTION_SIZE = 12
TITLE_SIZE = 18
LINE_GAP = 13


def escape_pdf_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def wrap_text(text: str, max_chars: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]

    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if len(candidate) <= max_chars:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def add_line(commands: list[str], text: str, x: int, y: int, font: str, size: int) -> None:
    commands.append("BT")
    commands.append(f"/{font} {size} Tf")
    commands.append(f"1 0 0 1 {x} {y} Tm")
    commands.append(f"({escape_pdf_text(text)}) Tj")
    commands.append("ET")


def build_content() -> list[tuple[str, str]]:
    return [
        ("title", "Viora - One-Page App Summary"),
        ("section", "What It Is"),
        (
            "body",
            "Viora is a Windows-focused AI automation assistant with a Typer CLI, a LangChain-based"
            " agent brain, and tool wrappers for browser, desktop, and todo actions."
        ),
        (
            "body",
            "It selects an LLM backend via VIORA_MODEL_PROVIDER and can persist chat logs, todos,"
            " and a browser profile locally."
        ),
        ("section", "Who It's For"),
        (
            "body",
            "Primary user: Windows users and automation enthusiasts who want to trigger everyday"
            " system, browser, and task workflows with natural-language commands."
        ),
        ("section", "What It Does"),
        ("bullet", "Runs interactive chat plus one-shot query execution from the CLI."),
        ("bullet", "Routes requests through rules, intent classification, and tool-calling reasoning."),
        ("bullet", "Automates web actions with Playwright/Edge: open, click, type, search, extract text."),
        ("bullet", "Controls Windows actions: open apps, get time, volume, clipboard, screenshots."),
        ("bullet", "Provides mouse and keyboard automation helpers through the Windows skills layer."),
        ("bullet", "Stores todos in data/organizer.json and interaction logs in data/memory.json."),
        ("bullet", "Supports Groq, Google Gemini, and Ollama backends in agent/brain.py."),
        ("section", "How It Works"),
        (
            "bullet",
            "User -> Viora.py Typer commands (chat, todo, todos, open, time) -> Brain.run().",
        ),
        (
            "bullet",
            "Brain first applies hard-coded rules, then a router model decides chat vs tool path.",
        ),
        (
            "bullet",
            "Tool requests are bound from skills/tools_factory.py and call BrowserSkills,"
            " WindowsSkills, TodoSkills, or GeneralSkills.",
        ),
        (
            "bullet",
            "Outputs return to the console; state persists in data/memory.json,"
            " data/organizer.json, and data/browser_profile/.",
        ),
        ("section", "How To Run"),
        ("bullet", "1. Install deps: pip install -r requirements.txt"),
        ("bullet", "2. Install browser runtime: playwright install chromium"),
        (
            "bullet",
            "3. Add .env with VIORA_MODEL_PROVIDER plus GROQ_API_KEY or GOOGLE_API_KEY.",
        ),
        ("bullet", "4. Start chat from the repo root: python Viora.py chat"),
        ("bullet", "5. README says python main.py chat; main.py is Not found in repo."),
        (
            "foot",
            "Repo gap: Ollama is referenced in agent/brain.py, but setup steps for it are Not found in repo.",
        ),
    ]


def render_pdf(output_path: Path) -> None:
    commands: list[str] = []
    y = TOP_START
    max_body_chars = 88
    max_bullet_chars = 81

    for kind, text in build_content():
        if kind == "title":
            add_line(commands, text, LEFT_MARGIN, y, HEAD_FONT, TITLE_SIZE)
            y -= 24
        elif kind == "section":
            y -= 6
            add_line(commands, text, LEFT_MARGIN, y, HEAD_FONT, SECTION_SIZE)
            y -= 16
        elif kind == "body":
            for line in wrap_text(text, max_body_chars):
                add_line(commands, line, LEFT_MARGIN, y, BODY_FONT, BODY_SIZE)
                y -= LINE_GAP
        elif kind == "bullet":
            wrapped = wrap_text(text, max_bullet_chars)
            add_line(commands, f"- {wrapped[0]}", LEFT_MARGIN + 8, y, BODY_FONT, BODY_SIZE)
            y -= LINE_GAP
            for continuation in wrapped[1:]:
                add_line(commands, continuation, LEFT_MARGIN + 20, y, BODY_FONT, BODY_SIZE)
                y -= LINE_GAP
        elif kind == "foot":
            y -= 4
            for line in wrap_text(text, 95):
                add_line(commands, line, LEFT_MARGIN, y, BODY_FONT, 8)
                y -= 10

        if y < BOTTOM_MARGIN:
            raise RuntimeError("Content exceeded one page; reduce copy.")

    content_stream = "\n".join(commands).encode("ascii")

    objects: list[bytes] = []
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objects.append(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    page = (
        f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] "
        f"/Resources << /Font << /{BODY_FONT} 4 0 R /{HEAD_FONT} 5 0 R >> >> "
        f"/Contents 6 0 R >>"
    ).encode("ascii")
    objects.append(page)
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    objects.append(
        b"<< /Length " + str(len(content_stream)).encode("ascii") + b" >>\nstream\n"
        + content_stream
        + b"\nendstream"
    )

    pdf = bytearray()
    pdf.extend(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref_start = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF\n"
        ).encode("ascii")
    )

    output_path.write_bytes(pdf)


if __name__ == "__main__":
    target = Path("Viora_app_summary.pdf")
    render_pdf(target)
    print(target.resolve())
