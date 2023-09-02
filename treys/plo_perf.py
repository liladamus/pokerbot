import time

from treys.treys import Deck
from treys.treys.evaluator import PLOEvaluator


def setup(n: int, m: int) -> tuple[list[list[int]], list[list[int]]]:

    deck = Deck()

    boards = []
    hands = []

    for _ in range(n):
        boards.append(deck.draw(m))
        hands.append(deck.draw(4))
        deck.shuffle()

    return boards, hands


n = 10000
cumtime = 0.0
evaluator = PLOEvaluator()
boards, hands = setup(n, 5)
for i in range(len(boards)):
    start = time.time()
    evaluator.evaluate(hands[i], boards[i])
    cumtime += (time.time() - start)

avg = float(cumtime / n)
print("9 card evaluation:")
print("[*] Treys: Average time per evaluation: %f" % avg)
print("[*] Treys: Evaluations per second = %f" % (1.0 / avg))

###

cumtime = 0.0
boards, hands = setup(n, 4)
for i in range(len(boards)):
    start = time.time()
    evaluator.evaluate(hands[i], boards[i])
    cumtime += (time.time() - start)

avg = float(cumtime / n)
print("8 card evaluation:")
print("[*] Treys: Average time per evaluation: %f" % avg)
print("[*] Treys: Evaluations per second = %f" % (1.0 / avg))

###

cumtime = 0.0
boards, hands = setup(n, 3)
for i in range(len(boards)):
    start = time.time()
    evaluator.evaluate(hands[i], boards[i])
    cumtime += (time.time() - start)

avg = float(cumtime / n)
print("7 card evaluation:")
print("[*] Treys: Average time per evaluation: %f" % avg)
print("[*] Treys: Evaluations per second = %f" % (1.0 / avg))
