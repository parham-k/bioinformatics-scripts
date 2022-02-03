import os
import re
import argparse
import matplotlib.pyplot as plt
from tabulate import tabulate
from adjustText import adjust_text

Results = dict[str, str]
ResultsTable = dict[str, Results]


def parse_args():
    description = "Report parser and additional plot generator from QUAST output."
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("path",
                        help="Path to QUAST evaluation results folder.")
    parser.add_argument("-o", help="Path to output folder.", default=".")
    parser.add_argument(
        "-stats",
        nargs='+',
        help="Statistics to show in output table.",
        default=[
            "N50", "NG50", "NGA50", "# misassemblies", "# local misassemblies",
            "Genome fraction (%)", "Total length"
        ],
    )
    parser.add_argument(
        "-scatter-x",
        help="Name of the statistic to show on the scatter plot's x axis.",
        default="# misassemblies")
    parser.add_argument(
        "-scatter-y",
        nargs='+',
        help="Statistic(s) to show on the scatter plot's y axis. " + \
            "Multiple names will generate multiple plots. " + \
                 "Join two stats with a dash to generate a line plot. " + \
                 "E.g. (default): -scatter-y NG50 NGA50 NGA50-NG50",
                 default=["NG50", "NGA50", "NGA50-NG50"])
    parser.add_argument("-table-style",
                        help="Tabulate output style",
                        default="jira")
    parser.add_argument("-mplstyle",
                        help="Path to (or name of) matplotlib style.",
                        default="bmh")
    parser.add_argument("-output-prefix",
                        help="Optional prefix for generated file names.")
    return parser.parse_args()


def parse_report(path: str, stats: list[str]) -> Results:
    stats = dict((k, '-') for k in stats)
    with open(path, "r") as fp:
        for line in map(str.strip, fp.readlines()):
            matches = re.findall(r"(.*?)\s\s+(.*)", line)
            if matches and matches[0][0] in stats:
                stats[matches[0][0]] = matches[0][1]
    return stats


def load_results(path: str, stats: list[str]) -> ResultsTable:
    results = dict()
    runs = list(sorted(os.listdir(path)))
    for run in runs:
        file_path = os.path.join(path, run, "report.txt")
        results[run] = parse_report(file_path, stats)
    return results


def write_table(results: ResultsTable, path: str, style: str, keys: list[str]):
    table = []
    for run, stats in results.items():
        row = [run]
        for key in keys:
            row.append(stats[key])
        table.append(row)
    table_str = tabulate(table, tablefmt=style, headers=keys)
    if style == "jira":
        table_str = table_str.replace("#", "No.")
    with open(path, 'w') as fp:
        fp.write(table_str)


def draw_scatter_plot(results: ResultsTable, stat_x: str, stat_y: str
                      or list[str, str], path: str, filename_prefix: str
                      or None):
    plt.clf()
    plt.figure(dpi=300)
    texts = []
    vl_x, vl_y0, vl_y1 = [], [], []
    for run, stats in results.items():
        if isinstance(stat_y, str):
            x = [float(stats[stat_x])]
            y = [float(stats[stat_y])]
        else:
            x = [float(stats[stat_x])] * 2
            y = [float(stats[stat_y[0]]), float(stats[stat_y[1]])]
            vl_x.append(x[0])
            vl_y0.append(y[0])
            vl_y1.append(y[1])
        plt.scatter(x, y, label=run)
        texts.append(plt.text(x[0], y[0], run))
    if vl_x:
        c = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        plt.vlines(vl_x, vl_y0, vl_y1, colors=c)
    plt.legend()
    plt.xlabel(stat_x)
    filename_prefix = filename_prefix or ""
    if isinstance(stat_y, str):
        plt.ylabel(stat_y)
        filename = filename_prefix + f'{stat_x}_vs_{stat_y}.jpg'
    else:
        plt.ylabel(f'{stat_y[0]}|———|{stat_y[1]}')
        filename = filename_prefix + f'{stat_x}_vs_{"-".join(stat_y)}.jpg'
    filename = filename.replace("# ", "")
    adjust_text(texts)
    out_path = os.path.join(path, filename)
    plt.savefig(out_path, bbox_inches='tight')


def main():
    args = parse_args()
    plt.style.use(args.mplstyle)
    results = load_results(args.path, args.stats)
    if args.output_prefix:
        table_out_path = os.path.join(args.o, args.output_prefix + 'table.txt')
    else:
        table_out_path = os.path.join(args.o, 'table.txt')
    write_table(results, table_out_path, args.table_style, args.stats)
    for stat_y in args.scatter_y:
        if '-' in stat_y:
            stat_y = stat_y.split('-')
        draw_scatter_plot(results, args.scatter_x, stat_y, args.o,
                          args.output_prefix)


if __name__ == "__main__":
    main()
