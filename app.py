import streamlit as st
import game  # Import các hàm từ game.py

# Khởi tạo bảng game
board = game.initialize_board()

st.title("2048 Game - Play Online!")
st.write("Use the buttons to move the tiles.")

# Hiển thị bảng 2048
st.table(board)

# Nút điều khiển
if st.button("Left"):
    board = game.move_left(board)
if st.button("Right"):
    board = game.move_right(board)
if st.button("Up"):
    board = game.move_up(board)
if st.button("Down"):
    board = game.move_down(board)

# Thêm số mới sau mỗi lượt
game.add_new_number(board)

# Cập nhật giao diện
st.table(board)
