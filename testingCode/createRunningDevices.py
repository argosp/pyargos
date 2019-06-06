import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--deviceType", dest="type" , help="The devices type", required=True)
parser.add_argument("--deviceName", dest="name" , help="The devices base name", required=True)
parser.add_argument("--amount", dest="amount" , help="The amount of devices", required=True)
parser.add_argument("--totalTime", dest="totalTime" , help="The total time in seconds", required=True)
args = parser.parse_args()

baseStr = 'python demo%s.py' % (args.type)

answer = ''

for i in range(int(args.amount)):
    answer += ('%s --deviceName %s%04d --dataAmount 1 --delayTime 1 --totalTime %s &\n' % (baseStr, args.name, i+1, args.totalTime))
    #answer +=('%s --deviceName %s%04d_10s --dataAmount 1 --delayTime 10 --totalTime %s &\n' % (baseStr, args.name, i+1, args.totalTime))

with open('runDevices.sh', 'w') as runDevicesFile:
    runDevicesFile.write(answer)
