import argparse
import random

args = argparse.ArgumentParser()
args.add_argument("-w", help="Seed weight", type=int, default=-1)
args.add_argument("-l", help="Seed length", type=int, required=True)
args.add_argument("-n", help="Number of seeds", type=int, required=True)
args.add_argument("--bash", help="Print as bash array", dest='bash', action='store_true')
args = args.parse_args()

if args.w > 0:
    for _ in range(args.n):
        s = ['1'] * (args.w // 2 - 1) + ['0'] * (args.l // 2 - args.w // 2)
        random.shuffle(s)
        seed = '1' + ''.join(s + s[::-1]) + '1'
        print('    "' + seed + '"' if args.bash else seed)
else:
    for _ in range(args.n):
        s = '1' + ''.join(str(random.randint(1, 3) % 2) for _ in range(args.l // 2 - 1))
        seed = s + (str(random.randint(1, 3) % 2) if args.l % 2 == 1 else '') + s[::-1]
        print('    "' + seed + '"' if args.bash else seed)
