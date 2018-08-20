# pomutils

## Random script fragments for Pommerman that may or may not be useful

### replay - replay a game from recorded start state and actions (game_state.json)
Load start state and all game actions and replays the game using pommerman step function.
By default verifies calculated board with board recorded in game file. (Only board is verified, not bombs, attributes ..)
Requires game files with intended actions recorded (recent change)
CURRENTLY ONLY for FFA GAME.
Could be used to prevent regressions on step function changes, verify simulators or inspected on how to drive pommerman's step function from data.


replay.py
 	--gamefile *file*
	--noverify
	--verbose
