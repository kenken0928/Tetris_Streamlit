#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import random
import time

# --- 定数・グローバル変数 ---
BOARD_WIDTH = 10
BOARD_HEIGHT = 20

# テトリミノの形状（各ブロックの相対座標）※回転状態ごとにリストで定義
TETROMINOS = {
    'I': [
        [(0, 0), (1, 0), (2, 0), (3, 0)],
        [(0, 0), (0, 1), (0, 2), (0, 3)]
    ],
    'O': [
        [(0, 0), (1, 0), (0, 1), (1, 1)]
    ],
    'T': [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)]
    ],
    'S': [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(0, 0), (0, 1), (1, 1), (1, 2)]
    ],
    'Z': [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(1, 0), (0, 1), (1, 1), (0, 2)]
    ],
    'J': [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)]
    ],
    'L': [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)]
    ]
}

# 各テトリミノの色
COLORS = {
    'I': 'cyan',
    'O': 'yellow',
    'T': 'purple',
    'S': 'green',
    'Z': 'red',
    'J': 'blue',
    'L': 'orange'
}

# --- ヘルパー関数 ---

def init_board():
    """空のボード（20x10）を生成する"""
    return [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

def new_piece():
    """新しいテトリミノを生成する"""
    piece_type = random.choice(list(TETROMINOS.keys()))
    rotation = 0
    shape = TETROMINOS[piece_type][rotation]
    piece_width = max(x for x, y in shape) + 1
    start_x = (BOARD_WIDTH - piece_width) // 2
    start_y = 0
    return {
        'type': piece_type,
        'rotation': rotation,
        'x': start_x,
        'y': start_y
    }

def get_piece_cells(piece):
    """現在のテトリミノの各ブロックの絶対座標を返す"""
    shape = TETROMINOS[piece['type']][piece['rotation']]
    return [(piece['x'] + dx, piece['y'] + dy) for dx, dy in shape]

def can_place(piece, board, new_x, new_y, new_rotation):
    """指定の位置・回転状態でテトリミノを配置可能かチェックする"""
    shape = TETROMINOS[piece['type']][new_rotation]
    for dx, dy in shape:
        x, y = new_x + dx, new_y + dy
        if x < 0 or x >= BOARD_WIDTH or y < 0 or y >= BOARD_HEIGHT or board[y][x] is not None:
            return False
    return True

def lock_piece(piece, board):
    """テトリミノをボードに固定する"""
    color = COLORS[piece['type']]
    for x, y in get_piece_cells(piece):
        if 0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT:
            board[y][x] = color

def clear_lines(board):
    """完成したラインを削除し、新しい空行を上部に追加する"""
    new_board = [row for row in board if any(cell is None for cell in row)]
    lines_cleared = BOARD_HEIGHT - len(new_board)
    for _ in range(lines_cleared):
        new_board.insert(0, [None for _ in range(BOARD_WIDTH)])
    return new_board, lines_cleared

def calculate_score(lines_cleared):
    """ラインクリア数に応じてスコアを計算する"""
    if lines_cleared == 1:
        return 10
    elif lines_cleared == 2:
        return 20
    elif lines_cleared == 3:
        return 50
    elif lines_cleared == 4:
        return 100
    return 0

def render_board(board, piece=None):
    """ボードをHTMLで描画する。現在のテトリミノがあれば、ボード上に重ねて表示する。"""
    board_copy = [row.copy() for row in board]
    if piece:
        color = COLORS[piece['type']]
        for x, y in get_piece_cells(piece):
            if 0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT:
                board_copy[y][x] = color
    
    cell_size = 30
    html = "<div style='font-family: monospace; line-height: 0;'>"
    for row in board_copy:
        for cell in row:
            color = cell if cell else '#eee'
            border = '#444' if cell else '#ccc'
            html += f"<div style='width:{cell_size}px; height:{cell_size}px; background-color:{color}; display:inline-block; border:1px solid {border};'></div>"
        html += "<br>"
    html += "</div>"
    return html

# --- ゲームの初期化 ---
st.title("Streamlit Tetris")

if 'board' not in st.session_state:
    st.session_state.board = init_board()
    st.session_state.current_piece = new_piece()
    st.session_state.game_over = False
    st.session_state.score = 0
    st.session_state.speed = 1.0  # 初期スピード
    st.session_state.last_drop_time = time.time()
    st.session_state.start_time = time.time()

# ゲームリセット用のボタン
if st.button("リセット"):
    st.session_state.board = init_board()
    st.session_state.current_piece = new_piece()
    st.session_state.game_over = False
    st.session_state.score = 0
    st.session_state.speed = 1.0
    st.session_state.last_drop_time = time.time()
    st.session_state.start_time = time.time()
    st.rerun()

if st.session_state.game_over:
    st.markdown("<h1>ゲームオーバー</h1>", unsafe_allow_html=True)
    st.stop()

# スコア表示
st.markdown(f"### スコア: {st.session_state.score}")

# --- 自動落下設定 ---
auto_drop = st.checkbox("自動落下 (Tick)", value=False)

# --- ボードの描画 ---
board_html = render_board(st.session_state.board, st.session_state.current_piece)
st.markdown(board_html, unsafe_allow_html=True)

# --- 操作用ボタン ---
st.markdown("### 操作")
col_left, col_right, col_rotate = st.columns(3)
move_left = col_left.button("左移動")
move_right = col_right.button("右移動")
rotate = col_rotate.button("回転")

down = st.button("下移動")

# --- ゲームロジック ---
updated = False

def move_down():
    new_y = st.session_state.current_piece['y'] + 1
    if can_place(st.session_state.current_piece, st.session_state.board, st.session_state.current_piece['x'], new_y, st.session_state.current_piece['rotation']):
        st.session_state.current_piece['y'] = new_y
    else:
        lock_piece(st.session_state.current_piece, st.session_state.board)
        st.session_state.board, lines_cleared = clear_lines(st.session_state.board)
        st.session_state.score += calculate_score(lines_cleared)
        new_piece_obj = new_piece()
        if not can_place(new_piece_obj, st.session_state.board, new_piece_obj['x'], new_piece_obj['y'], new_piece_obj['rotation']):
            st.session_state.game_over = True
        else:
            st.session_state.current_piece = new_piece_obj

# 一番下まで落とす処理
def drop_to_bottom():
    while can_place(st.session_state.current_piece, st.session_state.board, st.session_state.current_piece['x'], st.session_state.current_piece['y'] + 1, st.session_state.current_piece['rotation']):
        st.session_state.current_piece['y'] += 1
    move_down()

# ボタン操作
if move_left and can_place(st.session_state.current_piece, st.session_state.board, st.session_state.current_piece['x'] - 1, st.session_state.current_piece['y'], st.session_state.current_piece['rotation']):
    st.session_state.current_piece['x'] -= 1
    updated = True

if move_right and can_place(st.session_state.current_piece, st.session_state.board, st.session_state.current_piece['x'] + 1, st.session_state.current_piece['y'], st.session_state.current_piece['rotation']):
    st.session_state.current_piece['x'] += 1
    updated = True

new_rotation = (st.session_state.current_piece['rotation'] + 1) % len(TETROMINOS[st.session_state.current_piece['type']])
if rotate and can_place(st.session_state.current_piece, st.session_state.board, st.session_state.current_piece['x'], st.session_state.current_piece['y'], new_rotation):
    st.session_state.current_piece['rotation'] = new_rotation
    updated = True

if down:
    drop_to_bottom()
    updated = True

# 自動落下処理
def auto_drop_logic():
    current_time = time.time()
    if current_time - st.session_state.last_drop_time >= st.session_state.speed:
        move_down()
        st.session_state.last_drop_time = current_time

    elapsed_game_time = current_time - st.session_state.start_time
    if elapsed_game_time > 180:
        st.session_state.speed = max(0.1, st.session_state.speed - 0.1)
        st.session_state.start_time = current_time

if auto_drop:
    auto_drop_logic()
    updated = True

if updated:
    st.rerun()

