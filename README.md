
# A talking chess AI
 
## _powered by Jurassic-1 language model by AI21Labs Studio_


- [Running the game](#running-the-game)
- [How to play](#how-to-play)
- [Configuration](#configuration)

# Running the game

The game runs as a local web server. To play you need to run the server and browse to http://127.0.0.1:5000/.
The server will automatically move the pieces for the AI and give vocal feedback to the user.

You need to have `python > 3.7` and `pip` to install the dependencies and run the server. 

In order to run the server:

1. Install the python dependencies using pip:
```shell 
pip install -r requirements.txt
```
If you are running on Windows and the speech doesn't work, try to edit requirement.txt and change the version of pyttsx3 to 2.71.

2. Give running permission to the chess engine:
```shell
chmod +x engines/stockfish
```
3. Edit config.ini and put your AI21 Studio API key in the reserved place.
4. Start Flask's development server:
```shell
python play.py
```
***🎉 The server should be up and running locally on port 5000.***

# How to play?

- A new game starts immediately when the server runs. Human plays white. 
- Browse to http://127.0.0.1:5000/
- Click on a piece to move, then click on a target square. The AI makes its response automatically.
- From time to time the AI will give vocal feedback to the human moves. At the top of the board you can select the tone of the feedback (tutor or taunt)

# Configuration

You can change a few of the game's configuration parameters by editing config.ini:

1. AI21 studio API parameters.
```ini
api_key = <<your api key>>
url = https://api.ai21.com/studio/v1/j1-jumbo/complete 
#url = https://api.ai21.com/studio/v1/j1-large/complete
```
- `api_key` You AI21 studio API key.
- `url` The API url address. By default we use the url to J1-Jumbo model. Replace the mask to use J1-Large instead.

2. Speech parameters.
```ini
bad_move_threshold = 50
good_move_threshold = 10
max_time_between_speech = 12
```
- `bad_move_threshold` The minimum centipawn difference between the human's move and the best move to trigger a bad-move comment. 
- `good_move_threshold` The maximum centipawn difference between the human's move and the best move to trigger a good-move comment.
- `max_time_between_speech` Maximum seconds without any comment from the AI.

3. Speech tones.

   You can edit or add your own prompts to get a speaking opponent of your taste.

4. Chess engine.

   We are using Stockfish, the open source chess engine: https://stockfishchess.org/.
