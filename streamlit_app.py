# sudoku_app.py
import streamlit as st
import random
import copy

st.set_page_config(page_title="Sudoku d'anniversaire", layout="centered")

# ---------- Sudoku generator & solver (backtracking) ----------
def find_empty(board):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return r, c
    return None

def valid(board, num, pos):
    r, c = pos
    # row
    if any(board[r][j] == num for j in range(9) if j != c):
        return False
    # col
    if any(board[i][c] == num for i in range(9) if i != r):
        return False
    # box
    br, bc = 3*(r//3), 3*(c//3)
    for i in range(br, br+3):
        for j in range(bc, bc+3):
            if (i, j) != pos and board[i][j] == num:
                return False
    return True

def solve(board):
    empty = find_empty(board)
    if not empty:
        return True
    r, c = empty
    nums = list(range(1,10))
    for n in nums:
        if valid(board, n, (r,c)):
            board[r][c] = n
            if solve(board):
                return True
            board[r][c] = 0
    return False

def generate_full_board():
    board = [[0]*9 for _ in range(9)]
    # fill diagonal boxes first for speed
    def fill_box(r, c):
        nums = list(range(1,10))
        random.shuffle(nums)
        idx = 0
        for i in range(r, r+3):
            for j in range(c, c+3):
                board[i][j] = nums[idx]; idx += 1
    for k in range(0,9,3):
        fill_box(k, k)
    # solve to get a complete valid board
    solve(board)
    return board

def make_puzzle(full_board, holes=40):
    # holes = number of cells to remove (rough difficulty control)
    puzzle = copy.deepcopy(full_board)
    coords = [(r,c) for r in range(9) for c in range(9)]
    random.shuffle(coords)
    removed = 0
    for (r,c) in coords:
        if removed >= holes:
            break
        backup = puzzle[r][c]
        puzzle[r][c] = 0
        # Optionally check uniqueness here (expensive). We'll skip uniqueness check for simplicity.
        removed += 1
    return puzzle

# ---------- Session state initialization ----------
if "full_solution" not in st.session_state:
    st.session_state.full_solution = None
if "puzzle" not in st.session_state:
    st.session_state.puzzle = None
if "board" not in st.session_state:
    st.session_state.board = None
if "difficulty" not in st.session_state:
    st.session_state.difficulty = "Medium"

# ---------- UI ----------
st.title("🧩 Sudoku en Streamlit")

col1, col2, col3 = st.columns([1,2,1])
with col1:
    if st.button("Nouvelle grille"):
        # choose number of holes by difficulty
        diff = st.session_state.difficulty
        if diff == "Easy":
            holes = 35
        elif diff == "Medium":
            holes = 45
        else:  # Hard
            holes = 55
        full = generate_full_board()
        puzzle = make_puzzle(full, holes=holes)
        st.session_state.full_solution = full
        st.session_state.puzzle = puzzle
        st.session_state.board = copy.deepcopy(puzzle)
        st.success("Nouvelle grille générée !")
with col2:
    st.selectbox("Difficulté", ["Easy", "Medium", "Hard"], key="difficulty")
with col3:
    if st.button("Résoudre"):
        if st.session_state.full_solution is None:
            st.warning("Génère d'abord une grille (Nouvelle grille).")
        else:
            st.session_state.board = copy.deepcopy(st.session_state.full_solution)
            st.success("Grille résolue.")

st.markdown("**Instructions :** entrez des chiffres 1–9 dans les cases vides. Cliquez sur **Vérifier** pour tester la validité, **Indice** remplira une case correcte.")

# initialize a default puzzle on first load
if st.session_state.puzzle is None:
    # generate a default medium puzzle
    full = generate_full_board()
    puzzle = make_puzzle(full, holes=45)
    st.session_state.full_solution = full
    st.session_state.puzzle = puzzle
    st.session_state.board = copy.deepcopy(puzzle)

# Render grid
st.write("")  # spacing
grid_cols = []
for i in range(9):
    grid_cols.append(st.columns(9))

# We'll display the grid as interactive inputs; pre-filled cells disabled
for r in range(9):
    for c in range(9):
        key = f"cell_{r}_{c}"
        pre = st.session_state.puzzle[r][c]
        val = st.session_state.board[r][c]
        # value for text_input must be string
        if pre != 0:
            # prefilled -> disabled input showing number
            # using st.text_input disabled=True (available in new streamlit)
            grid_cols[r][c].text_input(
                label="",
                value=str(pre),
                key=key,
                disabled=True
            )
        else:
            # editable cell — show current value or empty
            current = "" if val == 0 else str(val)
            # limit input to 1 char, but we must sanitize later
            user = grid_cols[r][c].text_input(label="", value=current, key=key, max_chars=1)
            # sanitize and update board
            if user.strip() == "":
                st.session_state.board[r][c] = 0
            else:
                ch = user.strip()
                if ch.isdigit() and 1 <= int(ch) <= 9:
                    st.session_state.board[r][c] = int(ch)
                else:
                    # invalid input -> reset to blank (user will see it)
                    st.session_state.board[r][c] = 0

# Controls under the grid
cols = st.columns([1,1,1,1])
with cols[0]:
    if st.button("Vérifier"):
        if st.session_state.board is None:
            st.warning("Aucune grille chargée.")
        else:
            # check validity: no rule violation and maybe completeness
            bad_positions = []
            for r in range(9):
                for c in range(9):
                    val = st.session_state.board[r][c]
                    if val != 0:
                        # Temporarily remove this cell to check duplication
                        tmp = st.session_state.board[r][c]
                        st.session_state.board[r][c] = 0
                        if not valid(st.session_state.board, tmp, (r,c)):
                            bad_positions.append((r+1,c+1,tmp))
                        st.session_state.board[r][c] = tmp
            if bad_positions:
                msg = "Entrées invalides détectées aux positions (ligne, colonne, valeur):\n"
                for b in bad_positions:
                    msg += f"- Ligne {b[0]}, Col {b[1]} → {b[2]}\n"
                st.error(msg)
            else:
                # if no bad positions, check if complete
                if all(all(cell != 0 for cell in row) for row in st.session_state.board):
                    if st.session_state.board == st.session_state.full_solution:
                        st.success("Bravo 🎉 — grille complète et correcte, tu devrais définitivement jeter un coup d'oeil à https://happy-birthday-jp.streamlit.app/")
                    else:
                        st.warning("Complète mais incorrecte (quelques chiffres ne correspondent pas à la solution).")
                else:
                    st.success("Aucune violation des règles détectée jusque-là ✅")

with cols[1]:
    if st.button("Indice"):
        if st.session_state.full_solution is None:
            st.warning("Génère d'abord une grille.")
        else:
            # find an empty cell and fill with solution
            filled = False
            for r in range(9):
                for c in range(9):
                    if st.session_state.board[r][c] == 0:
                        st.session_state.board[r][c] = st.session_state.full_solution[r][c]
                        filled = True
                        break
                if filled:
                    break
            if filled:
                st.success("Un indice a été ajouté (une case remplie).")
            else:
                st.info("Aucune case vide restante.")

with cols[2]:
    if st.button("Réinitialiser grille"):
        # reset board to original puzzle (not the solution)
        st.session_state.board = copy.deepcopy(st.session_state.puzzle)
        st.info("Grille réinitialisée aux valeurs initiales.")

with cols[3]:
    if st.button("Exporter (copier)"):
        # create a simple textual export of current board
        text = ""
        for r in range(9):
            text += "".join(str(x) if x!=0 else "." for x in st.session_state.board[r]) + "\n"
        st.code(text, language="")

st.markdown("---")
st.caption("Ce Sudoku utilise un générateur/solveur backtracking simple (pour démonstration). "
           "Si tu veux : contrôle d'unicité de solution, meilleure UI (cases colorées), ou export PDF — je peux l'ajouter.")

# End of file
