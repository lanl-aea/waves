import argparse
import pathlib

from waves import qoi


def main():
    parser = argparse.ArgumentParser(help="Calculate QOIs")
    parser.add_argument("--weight", type=float)
    parser.add_argument("--height", type=float)
    parser.add_argument("--set", type=str)
    args = parser.parse_args()
    load = qoi.create_qoi(
        name="load",
        calculated=args.weight*args.height,
        units="N",
        long_name="Axial Load",
        description="Axial load through component XYZ",
        group=f"Assembly ABC Preload {args.name}",
        set_name=args.name,
        version="abcdef",
    qoi._write_qoi_set_to_csv(qoi.create_qoi_set([load, ]), f"{args.name}_qois.csv")
)



if __name__ == "__main__":
    main()
