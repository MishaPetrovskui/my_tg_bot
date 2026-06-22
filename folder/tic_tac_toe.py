import asyncio                           # [1]
from os import getenv                    # [1]
from dotenv import load_dotenv
from os import path
from aiogram.types import FSInputFile

# pip install aiogram
from aiogram import Bot, Dispatcher      # [1]
from aiogram.types import Message        # [1]
from aiogram.filters import Command

# pip install google-genai
from google import genai
from google.genai import types
from PromptBuilder import PromptBuilder

from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from random import random

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
]

EMOJI = {" ": "▫️", "X": "❌", "O": "⭕"}

def minimax(board: list[str], depth: int, is_maximizing: bool, ai_player: str, human_player: str) -> int:
    winner = TicTacToe.check_winner(board)
    if winner == ai_player:
        return 10 - depth
    if winner == human_player:
        return depth - 10
    if winner == "Draw":
        return 0

    if is_maximizing:
        best_score = float('-inf')
        for i in range(9):
            if board[i] == " ":
                board[i] = ai_player
                score = minimax(board, depth + 1, False, ai_player, human_player)
                board[i] = " "
                best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for i in range(9):
            if board[i] == " ":
                board[i] = human_player
                score = minimax(board, depth + 1, True, ai_player, human_player)
                board[i] = " "
                best_score = min(score, best_score)
        return best_score

class TicTacToe:
    @staticmethod
    def check_winer(board:list[str]):
        for a,b,c in WIN_LINES:
            if board[a] != " " and board[a] == board[b] == board[c]:
                return board[a]
            if board[a] == " ":
                return "Draw"
            return None

    @staticmethod
    def ai_choose_move(board: list[str], ai_player: str, human_player: str):
        empty_cells = [i for i, v in enumerate(board) if v == " "]

        if random.random():
            return random.choice(empty_cells)

        _, best_move = minimax(board, ai_player, ai_player=ai_player, human_player=human_player)
        return best_move

    @staticmethod
    def render_map(board: list[str]):
        kb = InlineKeyboardBuilder()
        for i, cell in enumerate(board):
            kb.button(text=EMOJI[cell], callback_data=f"ttt:{i}")
        kb.adjust(3, 3, 3)
        return kb.as_markup()

    @staticmethod
    async def finish_game(message: Message, board:list[str], winner:str):
        if winner == "Draw":
            text = "DRAW!!!"
        else:
            text = f"WINNER:{EMOJI[winner]}"
        await message.edit_text(text, reply_markup=TicTacToe.render_map(board))
