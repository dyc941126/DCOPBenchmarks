import os

from benchmarks.radar_problem import radar_problem
from benchmarks.randon_n_dcop import RandomNDCOP
from benchmarks.channel_allocation import ChannelAllocation
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', type=str, default='randomDCOP',
                        help='problem type to generate (randomDCOP|netRad|channelAllocation)')
    parser.add_argument('-f', type=str, help='destination file', required=True)
    parser.add_argument('-md', '--minimum_domain', type=int, default=2,
                        help='minimum domain size (applied only to randomDCOP)')
    parser.add_argument('-xd', '--maximum_domain', type=int, default=5,
                        help='maximum domain size (applied only to randomDCOP)')
    parser.add_argument('-ma', '--minimum_arity', type=int, default=2,
                        help='minimum arity (applied only to randomDCOP)')
    parser.add_argument('-xa', '--maximum_arity', type=int, default=5,
                        help='maximum arity (applied only to randomDCOP)')
    parser.add_argument('-fn', '--fac_num', type=int, default=10,
                        help='number of factor node (applied only to randomDCOP)')
    parser.add_argument('-mt', '--minimum_tightness', type=float, default=0.1,
                        help='minimum variable tightness (applied only to randomDCOP)')
    parser.add_argument('-xt', '--maximum_tightness', type=float, default=0.5,
                        help='maximum variable tightness (applied only to randomDCOP)')
    parser.add_argument('-mu', '--minimum_utility', type=float, default=0,
                        help='minimum utility value (applied only to randomDCOP)')
    parser.add_argument('-xu', '--maximum_utility', type=float, default=1000,
                        help='maximum utility value (applied only to randomDCOP')
    parser.add_argument('-r', '--row', type=int, default=6,
                        help='number of rows (applied to netRad and channelAllocation')
    parser.add_argument('-c', '--col', type=int, default=8,
                        help='number of columns (applied to netRad and channelAllocation')
    parser.add_argument('-np', type=int, default=48,
                        help='number of phenomena')
    parser.add_argument('-cn', '--channels', type=int, default=10,
                        help='number of channels (applied only to channelAllocation)')
    parser.add_argument('-ap', type=int, default=60, help='number of APs (applied only to channelAllocation)')
    parser.add_argument('-xp', '--maximum_power', type=float, default=510,
                        help='maximum power (applied only to channelAllocation)')
    parser.add_argument('-mp', '--minimum_power', type=float, default=490,
                        help='minimum power (applied only to channelAllocation)')
    parser.add_argument('-bkg', type=float, default=1, help='background noise')
    args = parser.parse_args()
    from pathlib import Path
    path = Path(args.f)
    p = path.parent
    f = path.name
    if args.t == 'randomDCOP':
        random_dcop = RandomNDCOP(args.fac_num, args.minimum_arity, args.maximum_arity, args.minimum_tightness,
                                  args.maximum_tightness, args.minimum_domain, args.maximum_domain,
                                  args.minimum_utility, args.maximum_utility)
        random_dcop.generate(p, f)
    elif args.t == 'netRad':
        cnt = int(args.np / 2)
        while not radar_problem(args.row, args.col, cnt, cnt, p, f):
            pass
    elif args.t == 'channelAllocation':
        channel = ChannelAllocation(args.channels, args.ap, args.row, args.col, args.maximum_power, args.minimum_power,
                                    args.bkg)
        channel.generate()
        channel.save(os.path.join(p, f))