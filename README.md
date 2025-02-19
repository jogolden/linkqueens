# LinkedIn Queens Solver!

[LinkedIn Queens](https://www.linkedin.com/games/queens/)

This uses [z3](https://github.com/Z3Prover/z3) to solve the LinkedIn Queens game! Smarter than 99% of 
CEOs, which does not mean anything.

A Queens game only actually has a single valid solution. In the future I plan on training a NN using RL self-play, and I have made some progress. Some ideas:
- Solving with SMT is near instant so can the NN be faster?
- The NN I have so far will make a valid decision that ends up not being part of the final solution. You can't be greedy. In this case you must backtrack for every single wrong move, so you are almost doing a bunch of depth first searching.
- I have noticed myself/humans will avoid this by using heuristics based on the regions, like they know this entire column is one region so it must be in there, but they don't know where yet... but this information is useful for later. Humans also will go down a path, but then quickly return and shuffle some things around but while keeping "partial solutions" discovered by going down that path even if the original placed queen was wrong.
- There are more strategies than just this! Brute force DFS with a NN is no better than the SMT/brute force I think.
- The game is a visual logic game, maybe an RNN/LSTM CNN would be best? I have just been playing with a large MLP poly model, softmax output (n * n) distribution of best placement move.

# Usage

1. Install the Chrome [Disable CSP](https://chromewebstore.google.com/detail/disable-content-security/ieelmcmcagommplceebfedjlakkhpden?hl=en) extension.
2. Navigate to [LinkedIn Queens](https://www.linkedin.com/games/queens/), do not start the game!
3. Enable CSP plugin, so the icon is showing and reload page.
4. Start the solver server using `server.sh`.
5. Inspect element on the webpage to bring up the console, paste the `inject.js` code.
6. ????
7. Profit.
