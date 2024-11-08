# 150.209.91.34
# get File4_anon.txt
files = [
    "tcp1.txt",
    "tcp2.txt",
    "tcp3.txt",
    "tcp4.txt",
]


def evaluate(path_file):
    with open(path_file, "r") as file:
        lines = [line.split() for line in file]

    time0 = lines[0][1]
    time1 = lines[-1][1]
    delay = float(time1) - float(time0)

    bytes = sum([int(line[5]) for line in lines])
    bits = 8 * bytes
    throughput = int(bits / delay)

    delay = round(delay, 4)

    return delay, throughput


if __name__ == "__main__":
    delays = []
    throughputs = []

    for file in files:
        delay, throughput = evaluate(file)
        delays.append(str(delay))
        throughputs.append(str(throughput))

    print(f"delays {" ".join(delays)}")
    print(f"throughputs {" ".join(throughputs)}")
