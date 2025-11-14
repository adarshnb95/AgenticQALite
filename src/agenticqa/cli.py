# src/agenticqa/cli.py
import typer
from agenticqa.config_loader import load_config
from agenticqa.reporting import build_report, print_summary
from agenticqa.core.runner import run_tests

app = typer.Typer()

@app.command()
def run(config: str = "agenticqa.yaml"):
    """
    Run AgenticQALite tests using the given config file.
    """
    cfg = load_config(config)
    results = run_tests(cfg)
    report = build_report(results)
    print_summary(report)

def main():
    app()

if __name__ == "__main__":
    main()