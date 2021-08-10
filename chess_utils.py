import chess
from chess import parse_square, Board
from chess.engine import Limit
from chess import PIECE_NAMES
from copy import deepcopy

limit = Limit(time=0.1)


def parse_san_move(san_move):
    assert len(san_move) == 4
    from_square = parse_square(san_move[:2])
    to_square = parse_square(san_move[2:])
    return from_square, to_square


def get_move_details(board, san_move):
    from_square, to_square = parse_san_move(san_move)
    piece = board.piece_at(from_square)
    piece_name = PIECE_NAMES[piece.piece_type]

    return piece_name, san_move[:2], san_move[2:]


def get_board_score(board, engine):
    return engine.analyse(board, limit)["score"].relative.cp


def get_white_score(board, engine):
    return get_board_score(board, engine)


def get_best_move(board, engine):
    copied_board = deepcopy(board)
    play = engine.play(copied_board, limit)
    return play.move, copied_board


def get_best_move_with_score(board, engine):
    best_move, new_board = get_best_move(board, engine)
    return best_move, get_white_score(new_board, engine)


# if __name__ == '__main__':
#     new_board = Board()
#     engine = chess.engine.SimpleEngine.popen_uci("./engines/stockfish")
#     print(make_and_analyze_user_move(new_board, engine, "e2e4"))