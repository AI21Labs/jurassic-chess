from configobj import ConfigObj
import sys
import threading
import requests
import chess
import chess.svg
import chess.polyglot
import time
import traceback
import chess.pgn
import chess.engine
from flask import Flask, Response, request
import pyttsx3
from chess_utils import get_white_score, get_best_move_with_score, get_move_details

JABBER_PROMPT = 'jabber'
GOOD_MOVE_PROMPT = 'good_move'
BAD_MOVE_PROMPT = 'bad_move'
prompts_types = [JABBER_PROMPT, GOOD_MOVE_PROMPT, BAD_MOVE_PROMPT]

app = Flask(__name__)


def make_and_analyze_user_move(board, move):
    score_before = get_white_score(board, engine)
    best_move, best_move_score = get_best_move_with_score(board, engine)

    best_move_piece_name, best_move_from_position, best_move_to_position = get_move_details(board, str(best_move))
    user_piece_name, user_from_position, user_to_position = get_move_details(board, move)

    board.push_san(move)

    user_score = -get_white_score(board, engine)

    return {
        "score_before": score_before,
        "user_piece_name": user_piece_name,
        "user_from_position": user_from_position,
        "user_to_position": user_to_position,
        "user_score": user_score,
        "best_move_piece_name": best_move_piece_name,
        "best_move_from_position": best_move_from_position,
        "best_move_to_position": best_move_to_position,
        "best_move_score": best_move_score
    }


class Speaker:
    def __init__(self):
        self.voice = 0
        self.texts_to_speak = []

    def set_voice(self, voice):
        self.voice = int(voice)

    def start(self):
        global _text_to_speak
        no_speak_counter = 0
        while True:
            if self.texts_to_speak:
                engine = pyttsx3.init()
                if engine._inLoop:
                    engine.endLoop()

                engine.setProperty('rate', 150)
                voices = engine.getProperty('voices')
                engine.setProperty('voice', voices[self.voice].id)

                no_speak_counter = 0

                _text_to_speak = self.texts_to_speak.pop(0)
                engine.say(_text_to_speak)
                engine.runAndWait()
            else:
                no_speak_counter += 1
            if no_speak_counter == max_time_between_speech:
                no_speak_counter = 0
                speak_jabber()
            else:
                time.sleep(1)

    def speak(self, text):
        self.texts_to_speak.append(text)


def speak(text):
    speaker.speak(text)


def machine_move():
    move = engine.play(board, chess.engine.Limit(time=1))
    board.push(move.move)


@app.route("/")
def main():
    global count, board, _text_to_speak

    ret = '<html><head>'
    ret += '<style>input {font-size: 20px; } button { font-size: 20px; }</style>'
    ret += '<script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.1/jquery.min.js"></script>'
    ret += """<script>function clicked(){
        alert("x:y");
    }
    $(document).ready(function() {
    $("img").on("click", function(event) {
        var x = event.pageX - this.offsetLeft;
        var y = event.pageY - this.offsetTop;
        x = Math.floor((x + 5) / 62.5)
        y =   Math.floor((y + 5) / 62.5)
        var r = Math.floor(Math.random() * 1000)
        $("img").attr("src",`/board.svg/?x=${x}&y=${y}&rand=${r}`);
    });
    
});

                </script>"""
    ret += '</head><body><br><h1 align=center>Talking AI Chess Tutor / Taunter</h1><br>'
    ret += """<form action="/tone/" method="post" align=center><label>Choose the speaker's style:</label>
    <select name='selectedtone' class="drpdwn" value=" " onchange='this.form.submit()'>"""
    ret += f"<option>{current_tone}</option>"
    for tone in prompts.keys():
        if tone != current_tone:
            ret += f"<option>{tone}</option>"
    ret += "</select></form>"
    ret += '<div style="display: flex;justify-content: center;align-items: center;flex-direction: column;">'
    ret += '<img onclick="clicked(evt)" width=510 height=510 src="/board.svg"></img></br>'
    ret += '<form action="/game/" method="post"><button name="New Game" type="submit">New Game</button></form>'
    ret += '<form action="/undo/" method="post"><button name="Undo" type="submit">Take Back Last Move</button></form>'
    ret += '</div>'
    return ret


_piece_from = None
_piece_to = None


@app.route("/board.svg/")
def board():
    global _piece_to, _piece_from
    x = request.args.get('x')
    y = request.args.get('y')
    if x and y:
        x = int(x)
        y = int(y)
        piece = chess.SQUARES[((7 - y) * 8) + x]
        if _piece_from and not _piece_to:
            for curr_move in board.legal_moves:
                if curr_move.to_square == piece and curr_move.from_square == _piece_from:
                    move(curr_move)
                    return Response(chess.svg.board(board=board, size=510), mimetype='image/svg+xml')
        set = []
        for curr_move in board.legal_moves:
            if curr_move.from_square == piece:
                _piece_from = piece
                _piece_to = None
                set.append(curr_move.to_square)
        if not set:
            _piece_from = None
            _piece_to = None
        return Response(chess.svg.board(board=board, squares=chess.SquareSet(set), size=510), mimetype='image/svg+xml')
    else:
        _piece_from = None
        _piece_to = None
        return Response(chess.svg.board(board=board, size=700), mimetype='image/svg+xml')


@app.route("/tone/", methods=['POST'])
def select_tone(selected_tone=None):
    global current_tone
    if selected_tone:
        current_tone = selected_tone
    else:
        current_tone = request.values.dicts[1]['selectedtone']
    if sys.platform == 'win32':
        speaker.set_voice(config['speech_styles'][current_tone]['win_voice'])
    else:
        speaker.set_voice(config['speech_styles'][current_tone]['mac_voice'])
    return main()


@app.route("/move/")
def move(sun_move=None):
    try:
        move = None
        if sun_move:
            move = str(sun_move)
        else:
            move = request.args.get('move', default="")
        res = make_and_analyze_user_move(board, move)
        speak_after_human_move(res)

    except Exception:
        traceback.print_exc()
    try:
        machine_move()
    except Exception:
        traceback.print_exc()
    return main()


@app.route("/game/", methods=['POST'])
def game():
    board.reset()
    return main()


@app.route("/undo/", methods=['POST'])
def undo():
    try:
        board.pop()
    except Exception:
        traceback.print_exc()
    return main()


def j1_generate_and_speak(prompt):
    retry = 2
    while retry > 0:
        try:
            generate = requests.post(config['ai21']['url'],
                                     headers={"Authorization": "Bearer " + config['ai21']['api_key']},
                                     json={
                                         "model": config['ai21']['model'],
                                         "prompt": prompt,
                                         "numResults": 1,
                                         "maxTokens": 64,
                                         "stopSequences": ["\n"],
                                         "topKReturn": 0,
                                         "temperature": 0.8
                                     }
                                     ).json()
            if len(generate)==1:
                print(generate['detail'])
            else:
                speak(generate['completions'][0]['data']['text'])
            break
        except:
            retry -= 1
            continue


def speak_jabber():
    threading.Thread(target=j1_generate_and_speak, args=(prompts[current_tone][JABBER_PROMPT],)).start()


def speak_after_human_move(move_analysis):
    user_move_score = move_analysis['user_score']
    best_move_score = move_analysis['best_move_score']
    if best_move_score >= user_move_score + bad_move_threshold:
        speak_bad_move(move_analysis)
    elif best_move_score <= user_move_score + good_move_threshold:
        speak_good_move(move_analysis)


def speak_good_move(move_analysis):
    piece = f"{move_analysis['user_piece_name']}"
    prompt = prompts[current_tone][GOOD_MOVE_PROMPT].format(piece)
    threading.Thread(target=j1_generate_and_speak, args=(prompt,)).start()


def speak_bad_move(move_analysis):
    user_piece = move_analysis['user_piece_name']
    best_piece = move_analysis['best_move_piece_name']
    alternative = f"{best_piece} to {move_analysis['best_move_to_position']}"
    piece = f"{user_piece} to {move_analysis['user_to_position']}"
    prompt = prompts[current_tone][BAD_MOVE_PROMPT].format(piece, alternative)
    threading.Thread(target=j1_generate_and_speak, args=(prompt,)).start()


if __name__ == '__main__':
    config = ConfigObj("config.ini")

    if sys.platform == 'win32':
        chess_engine = config['chess_engine']['win']
    else:
        chess_engine = config['chess_engine']['mac']
    engine = chess.engine.SimpleEngine.popen_uci(chess_engine)

    _text_to_speak = ""

    speaker = Speaker()

    bad_move_threshold = int(config['speech']['bad_move_threshold'])
    good_move_threshold = int(config['speech']['good_move_threshold'])
    max_time_between_speech = int(config['speech']['max_time_between_speech'])
    prompts = {}
    for tone in config['speech_styles'].sections:
        prompts[tone] = {}
        for p_type in prompts_types:
            with open(config['speech_styles'][tone]['prompts_path'] + p_type + "_prompt.txt") as prompt_file:
                prompts[tone][p_type] = "".join(prompt_file.readlines())
    current_tone = list(prompts.keys())[0]
    if sys.platform == 'win32':
        speaker.set_voice(config['speech_styles'][current_tone]['win_voice'])
    else:
        speaker.set_voice(config['speech_styles'][current_tone]['mac_voice'])

    speaker_thread = threading.Thread(target=speaker.start, args=())
    speaker_thread.start()

    # webbrowser.open("http://127.0.0.1:5000/")
    board = chess.Board()

    app.run()
