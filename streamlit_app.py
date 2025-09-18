import streamlit as st
import random
import copy

st.set_page_config(page_title="Sudoku pour JP", layout="centered")

# ----------------- Sudoku utils -----------------
def find_empty(board):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return r, c
    return None

def valid(board, num, pos):
    r, c = pos
    # ligne
    for j in range(9):
        if board[r][j] == num and j != c:
            return False
    # colonne
    for i in range(9):
        if board[i][c] == num and i != r:
            return False
    # bloc 3x3
    br, bc = 3*(r//3), 3*(c//3)
    for i in range(br, br+3):
        for j in range(bc, bc+3):
            if board[i][j] == num and (i, j) != pos:
                return False
    return True

def solve(board):
    empty = find_empty(board)
    if not empty:
        return True
    r, c = empty
    for n in range(1, 10):
        if valid(board, n, (r, c)):
            board[r][c] = n
            if solve(board):
                return True
            board[r][c] = 0
    return False

def count_solutions(board, limit=2):
    """Compte les solutions possibles. Arrête si >= limit (optimisation)."""
    empty = find_empty(board)
    if not empty:
        return 1
    r, c = empty
    total = 0
    for n in range(1, 10):
        if valid(board, n, (r, c)):
            board[r][c] = n
            total += count_solutions(board, limit)
            board[r][c] = 0
            if total >= limit:
                break
    return total

def generate_full_board():
    board = [[0]*9 for _ in range(9)]
    # remplir diagonales
    def fill_box(r, c):
        nums = list(range(1,10))
        random.shuffle(nums)
        idx = 0
        for i in range(r, r+3):
            for j in range(c, c+3):
                board[i][j] = nums[idx]; idx += 1
    for k in range(0,9,3):
        fill_box(k, k)
    solve(board)
    return board

def make_puzzle(full_board, holes=45, ensure_unique=True):
    puzzle = copy.deepcopy(full_board)
    coords = [(r,c) for r in range(9) for c in range(9)]
    random.shuffle(coords)
    removed = 0
    for (r,c) in coords:
        if removed >= holes:
            break
        backup = puzzle[r][c]
        puzzle[r][c] = 0
        if ensure_unique:
            test_board = copy.deepcopy(puzzle)
            if count_solutions(test_board) != 1:
                puzzle[r][c] = backup
                continue
        removed += 1
    return puzzle

# ----------------- Session state -----------------
if "full_solution" not in st.session_state:
    st.session_state.full_solution = None
if "puzzle" not in st.session_state:
    st.session_state.puzzle = None
if "board" not in st.session_state:
    st.session_state.board = None
if "difficulty" not in st.session_state:
    st.session_state.difficulty = "Hard"
if "message" not in st.session_state:
    st.session_state.message = ""

# ----------------- UI -----------------
st.title("🧩 Etape 1 de l'escape game 1 : le sudoku ")

col1, col2, col3 = st.columns([1,2,1])
with col1:
    if st.button("Nouvelle grille"):
        diff = st.session_state.difficulty
        holes = { "Hard": 54}[diff]
        full = generate_full_board()
        puzzle = make_puzzle(full, holes=holes, ensure_unique=True)
        st.session_state.full_solution = full
        st.session_state.puzzle = puzzle
        st.session_state.board = copy.deepcopy(puzzle)
        st.session_state.message = "Nouvelle grille générée (solution unique)."
with col2:
    st.selectbox("Difficulté", ["Hard"], key="difficulty")
with col3:
    if st.button("Résoudre"):
        if st.session_state.full_solution is None:
            st.warning("Génère d'abord une grille.")
        else:
            st.session_state.board = copy.deepcopy(st.session_state.full_solution)
            st.session_state.message = "Grille résolue."

if st.session_state.message:
    st.info(st.session_state.message)

if st.session_state.puzzle is None:
    full = generate_full_board()
    puzzle = make_puzzle(full, holes=45, ensure_unique=True)
    st.session_state.full_solution = full
    st.session_state.puzzle = puzzle
    st.session_state.board = copy.deepcopy(puzzle)

# ----------------- CSS -----------------
css = "<style>"
css += """
input[aria-label^="cell_"]{
  width:48px;
  height:48px;
  text-align:center;
  font-size:20px;
  font-weight:600;
  border-radius:2px;
  outline:none;
  box-sizing:border-box;
}
input[aria-label^="cell_"]::placeholder { color: #bbb; }
input[aria-label^="cell_"][disabled] {
  background: #f2f2f2;
  color: #111;
}
"""
for r in range(9):
    for c in range(9):
        top = "3px solid #222" if r % 3 == 0 else "1px solid #999"
        left = "3px solid #222" if c % 3 == 0 else "1px solid #999"
        bottom = "3px solid #222" if r == 8 else "1px solid #999"
        right = "3px solid #222" if c == 8 else "1px solid #999"
        selector = f'input[aria-label="cell_{r}_{c}"]'
        css += f"""
{selector} {{
  border-top: {top};
  border-left: {left};
  border-bottom: {bottom};
  border-right: {right};
}}
"""
css += "</style>"
st.markdown(css, unsafe_allow_html=True)

# ----------------- Render grid -----------------
for r in range(9):
    cols = st.columns(9, gap="small")
    for c in range(9):
        key = f"cell_{r}_{c}"
        pre = st.session_state.puzzle[r][c]
        val = st.session_state.board[r][c]
        if pre != 0:
            cols[c].text_input(label="", value=str(pre), key=key, disabled=True, label_visibility="collapsed")
        else:
            current = "" if val == 0 else str(val)
            user = cols[c].text_input(label="", value=current, key=key, max_chars=1, label_visibility="collapsed", placeholder=" ")
            if user.strip() == "":
                st.session_state.board[r][c] = 0
            else:
                ch = user.strip()
                if ch.isdigit() and 1 <= int(ch) <= 9:
                    st.session_state.board[r][c] = int(ch)
                else:
                    st.session_state.board[r][c] = 0

# ----------------- Controls -----------------
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("Vérifier"):
        bad = []
        for r in range(9):
            for c in range(9):
                v = st.session_state.board[r][c]
                if v != 0:
                    tmp = st.session_state.board[r][c]
                    st.session_state.board[r][c] = 0
                    if not valid(st.session_state.board, tmp, (r,c)):
                        bad.append((r+1, c+1, tmp))
                    st.session_state.board[r][c] = tmp
        if bad:
            st.error("Erreurs : " + ", ".join([f"(L{b[0]},C{b[1]}={b[2]})" for b in bad]))
        else:
            if all(all(cell != 0 for cell in row) for row in st.session_state.board):
                if st.session_state.board == st.session_state.full_solution:
                    st.success("🎉 Bravo, grille correcte et complète, tu devrais jeter un coup d'oeil au site : https://happy-birthday-jp.streamlit.app/")
                else:
                    st.warning("Grille complète mais incorrecte.")
            else:
                st.success("Aucune erreur détectée pour l’instant ✅")
with c2:
    if st.button("Indice"):
            st.info("Pas d'indice, la triche n'est pas autorisé chez les ORY")

with c3:
    if st.button("Réinitialiser"):
        st.session_state.board = copy.deepcopy(st.session_state.puzzle)
        st.info("Grille réinitialisée.")
with c4:
    if st.button("Exporter texte"):
        text = ""
        for r in range(9):
            text += "".join(str(x) if x!=0 else "." for x in st.session_state.board[r]) + "\n"
        st.code(text, language="")
