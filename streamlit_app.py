# sudoku_streamlit.py
import streamlit as st
import random
import copy

st.set_page_config(page_title="Sudoku extrêment dur", layout="centered")

# ----------------- Sudoku generator & solver (backtracking) -----------------
def find_empty(board):
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                return r, c
    return None

def valid(board, num, pos):
    r, c = pos
    # row
    for j in range(9):
        if board[r][j] == num and j != c:
            return False
    # col
    for i in range(9):
        if board[i][c] == num and i != r:
            return False
    # box
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

def generate_full_board():
    board = [[0]*9 for _ in range(9)]
    # fill diagonal boxes to speed up
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

def make_puzzle(full_board, holes=45):
    puzzle = copy.deepcopy(full_board)
    coords = [(r,c) for r in range(9) for c in range(9)]
    random.shuffle(coords)
    removed = 0
    for (r,c) in coords:
        if removed >= holes:
            break
        backup = puzzle[r][c]
        puzzle[r][c] = 0
        # skipping uniqueness check for speed (can be added)
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

# ----------------- Top UI -----------------
st.title("🧩 Sudoku — génération + UI stylée")

col1, col2, col3 = st.columns([1,2,1])
with col1:
    if st.button("Nouvelle grille"):
        diff = st.session_state.difficulty
        holes = {"Easy": 36, "Medium": 45, "Hard": 54}[diff]
        full = generate_full_board()
        puzzle = make_puzzle(full, holes=holes)
        st.session_state.full_solution = full
        st.session_state.puzzle = puzzle
        st.session_state.board = copy.deepcopy(puzzle)
        st.session_state.message = "Nouvelle grille générée."
with col2:
    st.selectbox("Difficulté", ["Hard"], key="difficulty")
with col3:
    if st.button("Résoudre"):
        if st.session_state.full_solution is None:
            st.warning("Génère d'abord une grille.")
        else:
            st.session_state.board = copy.deepcopy(st.session_state.full_solution)
            st.session_state.message = "Grille résolue."

st.markdown("**Instructions :** clique sur une case vide et tape 1–9. Utilise *Vérifier*, *Indice*, *Réinitialiser* selon besoin.")
if st.session_state.message:
    st.info(st.session_state.message)

# Initialize default puzzle if none
if st.session_state.puzzle is None:
    full = generate_full_board()
    puzzle = make_puzzle(full, holes=45)
    st.session_state.full_solution = full
    st.session_state.puzzle = puzzle
    st.session_state.board = copy.deepcopy(puzzle)

# ----------------- CSS for styling each input by aria-label (key) -----------------
# We'll generate CSS rules targeting input elements created by st.text_input.
css = "<style>"
# default style for all cells
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
# add thick separators for 3x3 blocks by setting border sides individually
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

# ----------------- Render grid using st.columns and st.text_input -----------------
# We'll create a 9x9 of inputs bound to keys like "cell_r_c"
for r in range(9):
    cols = st.columns(9, gap="small")
    for c in range(9):
        key = f"cell_{r}_{c}"
        pre = st.session_state.puzzle[r][c]
        val = st.session_state.board[r][c]
        # show prefilled as disabled input
        if pre != 0:
            # must pass string value
            cols[c].text_input(label="", value=str(pre), key=key, disabled=True, label_visibility="collapsed")
        else:
            current = "" if val == 0 else str(val)
            user = cols[c].text_input(label="", value=current, key=key, max_chars=1, label_visibility="collapsed", placeholder=" ")
            # sanitize and update board
            if user.strip() == "":
                st.session_state.board[r][c] = 0
            else:
                ch = user.strip()
                if ch.isdigit() and 1 <= int(ch) <= 9:
                    st.session_state.board[r][c] = int(ch)
                else:
                    # invalid input -> reset to blank
                    st.session_state.board[r][c] = 0

# ----------------- Controls -----------------
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("Vérifier"):
        if st.session_state.board is None:
            st.error("Aucune grille chargée.")
        else:
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
                msg = "Entrées invalides (ligne, col, valeur): " + ", ".join([f"({b[0]},{b[1]}→{b[2]})" for b in bad])
                st.error(msg)
            else:
                if all(all(cell != 0 for cell in row) for row in st.session_state.board):
                    if st.session_state.board == st.session_state.full_solution:
                        st.success("Bravo 🎉 — grille complète et correcte tu devrais passer à la prochaine étape sur https://happy-birthday-jp.streamlit.app/")
                    else:
                        st.warning("Grille complète mais incorrecte (quelques chiffres ne correspondent pas).")
                else:
                    st.success("Aucune violation détectée pour l'instant ✅")
with c2:
    if st.button("Indice"):
        if st.session_state.full_solution is None:
            st.warning("Génère d'abord une grille.")
        else:
            st.session_state.message = "ous n'avez pa le droit à un indice, la triche n'espas autorisé chez les ORY."
with c3:
    if st.button("Réinitialiser"):
        st.session_state.board = copy.deepcopy(st.session_state.puzzle)
        st.session_state.message = "Grille réinitialisée."
with c4:
    if st.button("Copier grille texte"):
        text = ""
        for r in range(9):
            text += "".join(str(x) if x!=0 else "." for x in st.session_state.board[r]) + "\n"
        st.code(text, language="")
        st.session_state.message = "Grille affichée ci-dessus (copiable)."

# Footer note
st.markdown("---")
st.caption("Remarques : le générateur n'effectue pas de vérification d'unicité de solution (plus coûteux). "
           "Si tu veux : ajout d'un chrono, sauvegarde, validation en live (coloration des erreurs) ou contrôle d'unicité — dis-moi laquelle ajouter et je la fournis.")

