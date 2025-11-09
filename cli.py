"""Command-line interface for the Personal API Security Tester."""
import json
from typing import List

import click
from loguru import logger

from apisec_tester import core, report


@click.group()
def cli():
    """Personal API Security Tester CLI"""
    pass


@cli.command()
@click.option("--endpoint", "endpoints", multiple=True, required=True,
              help="One or more endpoints to test. Provide multiple times.")
@click.option("--output", default="report.json", help="JSON output file path")
def run(endpoints: List[str], output: str):
    """Run checks against the given endpoints and produce a report."""
    logger.info("Starting checks for {} endpoints", len(endpoints))
    all_results = []
    for ep in endpoints:
        logger.info("Running checks for {}", ep)
        results = core.run_all_checks(ep)
        all_results.extend(results)
    # write report
    report.write_report(all_results, json_path=output, txt_path=output.replace('.json', '.txt'))
    click.echo(f"Wrote report to {output} and {output.replace('.json', '.txt')}")


@cli.command()
def interactive():
    """Simple interactive UI to enter endpoints and run checks."""
    click.echo("Personal API Security Tester — interactive mode")
    endpoints = []
    while True:
        ep = click.prompt("Enter endpoint (blank to finish)", default="", show_default=False)
        if not ep:
            break
        endpoints.append(ep)
    if not endpoints:
        click.echo("No endpoints provided — exiting.")
        return
    click.echo(f"Running quick checks for {len(endpoints)} endpoint(s)...")
    all_results = []
    for ep in endpoints:
        click.echo(f" - {ep}")
        r = core.run_all_checks(ep)
        all_results.extend(r)
    # show summary to console
    summary = report.summarize(all_results)
    click.echo("\n---\n")
    click.echo(summary)
    # offer to save
    if click.confirm("Save report to report.json?"):
        report.write_report(all_results, json_path="report.json", txt_path="report.txt")
        click.echo("Saved report.json and report.txt")


if __name__ == "__main__":
    cli()
