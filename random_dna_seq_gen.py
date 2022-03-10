import os
import random
import argparse
from tqdm import tqdm

ALPHABET = ('A', 'C', 'G', 'T')


def parse_args():
    args = argparse.ArgumentParser()
    args.add_argument("-n", help="Number of reads [1_000_000]", default=10**6)
    args.add_argument("-l", help="Read size [1000]", default=1000)
    args.add_argument("-o", help="Output file [data.fa]", default="data.fa")
    return args.parse_args()


def generate_read(read_len: int) -> str:
    return ''.join(random.choices(ALPHABET, k=read_len))


def generate_data(num_reads: int, read_len: int) -> list[str]:
    data = []
    for _ in tqdm(range(num_reads), desc='GENERATING DATA'):
        data.append(generate_read(read_len))
    return data


def write_data(data: list[str], out_path: str):
    with open(out_path, 'w') as fp:
        for i, read in tqdm(enumerate(data), desc='WRITING TO FILE'):
            fp.write(f'>r{i}' + os.linesep + read + os.linesep)


def main():
    args = parse_args()
    write_data(generate_data(args.n, args.l), args.o)


if __name__ == '__main__':
    main()
