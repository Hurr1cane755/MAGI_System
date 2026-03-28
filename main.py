import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import config
from magi import Balthasar, Caspar, Melchior

# ANSI 颜色代码
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

BG_BLACK = "\033[40m"

# Agent 专属颜色
COLOR_BALTHASAR = CYAN
COLOR_MELCHIOR = MAGENTA
COLOR_CASPAR = YELLOW
COLOR_SYSTEM = GREEN


def width() -> int:
    try:
        import shutil
        return min(shutil.get_terminal_size().columns, 80)
    except Exception:
        return 80


def divider(char: str = "─", color: str = DIM) -> str:
    return f"{color}{char * width()}{RESET}"


def header_box(title: str, color: str = WHITE) -> str:
    w = width()
    inner = w - 2
    top = f"╔{'═' * inner}╗"
    mid = f"║{title.center(inner)}║"
    bot = f"╚{'═' * inner}╝"
    return f"{color}{BOLD}{top}\n{mid}\n{bot}{RESET}"


def section_box(agent_name: str, role: str, content: str, color: str) -> str:
    w = width()
    inner = w - 2
    label = f" ◆ {agent_name} [{role}] "
    top = f"╔{label}{'═' * (inner - len(label))}╗"
    bot = f"╚{'═' * inner}╝"

    lines = []
    for line in content.strip().splitlines():
        # 简单换行适配
        while len(line) > inner - 2:
            lines.append(f"║ {line[:inner-2]} ║")
            line = line[inner - 2:]
        lines.append(f"║ {line:<{inner - 2}} ║")

    body = "\n".join(lines)
    return f"{color}{BOLD}{top}{RESET}\n{color}{body}{RESET}\n{color}{BOLD}{bot}{RESET}"


def spinner_task(label: str, stop_event: threading.Event, color: str) -> None:
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    i = 0
    while not stop_event.is_set():
        frame = frames[i % len(frames)]
        print(f"\r{color}{BOLD}{frame} {label}...{RESET}", end="", flush=True)
        stop_event.wait(0.1)
        i += 1
    print(f"\r{' ' * (len(label) + 10)}\r", end="", flush=True)


def run_with_spinner(label: str, color: str, fn, *args):
    stop = threading.Event()
    t = threading.Thread(target=spinner_task, args=(label, stop, color), daemon=True)
    t.start()
    try:
        result = fn(*args)
    finally:
        stop.set()
        t.join()
    return result


def print_nerv_banner(mock_mode: bool) -> None:
    banner = r"""
  ███╗   ███╗ █████╗  ██████╗ ██╗      ██╗     ██╗███╗   ██╗██╗  ██╗
  ████╗ ████║██╔══██╗██╔════╝ ██║      ██║     ██║████╗  ██║██║ ██╔╝
  ██╔████╔██║███████║██║  ███╗██║█████╗██║     ██║██╔██╗ ██║█████╔╝
  ██║╚██╔╝██║██╔══██║██║   ██║██║╚════╝██║     ██║██║╚██╗██║██╔═██╗
  ██║ ╚═╝ ██║██║  ██║╚██████╔╝██║      ███████╗██║██║ ╚████║██║  ██╗
  ╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝      ╚══════╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝"""
    print(f"{GREEN}{BOLD}{banner}{RESET}")
    print(f"{DIM}{'Multi-Agent General Intelligence — Decision System v0.1'.center(width())}{RESET}")
    mode_label = f"{'⚠  MOCK MODE — No real API calls':^{width()}}" if mock_mode else f"{'● LIVE MODE':^{width()}}"
    mode_color = YELLOW if mock_mode else GREEN
    print(f"{mode_color}{BOLD}{mode_label}{RESET}")
    print(divider("═", GREEN))


def main() -> None:
    print_nerv_banner(config.mock_mode)

    # 获取问题
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        print(f"\n{WHITE}{BOLD}请输入决策问题：{RESET}")
        try:
            question = input(f"{CYAN}▶ {RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{RED}已中止。{RESET}")
            sys.exit(0)

    if not question:
        print(f"{RED}错误：问题不能为空。{RESET}")
        sys.exit(1)

    print(f"\n{divider()}")
    print(f"{WHITE}{BOLD}  决策问题：{RESET}{question}")
    print(f"{divider()}\n")

    # 初始化 Agents
    balthasar = Balthasar(api_key=config.anthropic_api_key, mock_mode=config.mock_mode)
    melchior = Melchior(api_key=config.google_api_key, mock_mode=config.mock_mode)
    caspar = Caspar(api_key=config.openai_api_key, mock_mode=config.mock_mode)

    # 并行调用 Balthasar 和 Melchior
    print(f"{COLOR_SYSTEM}{BOLD}[ MAGI SYSTEM ] 启动并行分析...{RESET}\n")

    results: dict[str, str] = {}
    errors: dict[str, str] = {}

    def run_agent(agent, q):
        try:
            return agent.name, agent.analyze(q)
        except Exception as e:
            return agent.name, None, str(e)

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(balthasar.analyze, question): balthasar,
            executor.submit(melchior.analyze, question): melchior,
        }

        # 显示进度
        active: dict = {}
        stops: dict = {}

        for fut, agent in futures.items():
            stop = threading.Event()
            stops[fut] = stop
            color = COLOR_BALTHASAR if agent.name == "BALTHASAR" else COLOR_MELCHIOR
            t = threading.Thread(
                target=spinner_task,
                args=(f"{agent.name} 分析中", stop, color),
                daemon=True,
            )
            active[fut] = t
            t.start()

        for fut in as_completed(futures):
            agent = futures[fut]
            stops[fut].set()
            active[fut].join()
            try:
                results[agent.name] = fut.result()
                print(f"{GREEN}✔ {agent.name} 完成{RESET}")
            except Exception as e:
                errors[agent.name] = str(e)
                print(f"{RED}✘ {agent.name} 失败: {e}{RESET}")

    print()

    # 输出 Balthasar 结果
    if "BALTHASAR" in results:
        print(section_box("BALTHASAR", "理性分析", results["BALTHASAR"], COLOR_BALTHASAR))
        print()

    # 输出 Melchior 结果
    if "MELCHIOR" in results:
        print(section_box("MELCHIOR", "感性分析", results["MELCHIOR"], COLOR_MELCHIOR))
        print()

    # 调用 Caspar 仲裁
    print(f"{COLOR_SYSTEM}{BOLD}[ MAGI SYSTEM ] 移交 CASPAR 进行最终仲裁...{RESET}\n")

    balthasar_out = results.get("BALTHASAR", "（分析失败）")
    melchior_out = results.get("MELCHIOR", "（分析失败）")

    try:
        caspar_result = run_with_spinner(
            "CASPAR 仲裁中",
            COLOR_CASPAR,
            caspar.analyze_with_context,
            question,
            balthasar_out,
            melchior_out,
        )
        print(f"{GREEN}✔ CASPAR 裁决完成{RESET}\n")
        print(section_box("CASPAR", "仲裁决策", caspar_result, COLOR_CASPAR))
    except Exception as e:
        print(f"{RED}✘ CASPAR 失败: {e}{RESET}")

    print(f"\n{divider('═', GREEN)}")
    print(f"{COLOR_SYSTEM}{BOLD}{'[ MAGI SYSTEM ] 决策流程完成'.center(width())}{RESET}")
    print(f"{divider('═', GREEN)}\n")


if __name__ == "__main__":
    main()
