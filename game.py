import requests
from tkinter import *
from tkinter import messagebox
import firebase_admin
from firebase_admin import credentials, db
import os
import random



# Khởi tạo Firebase với Admin SDK
# Lấy đường dẫn tương đối đến thư mục hiện tại
current_dir = os.path.dirname(__file__)

# Tạo đường dẫn tương đối tới file JSON trong folder 2048_game_new
json_path = os.path.join(current_dir, "game2048.json")

# Khởi tạo Firebase với Admin SDK
cred = credentials.Certificate(json_path)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://game2048-3d6f3-default-rtdb.firebaseio.com/'  # Thay bằng URL của Firebase Realtime Database
})

# Hàm kiểm tra kết nối internet
def check_internet():
    url = "http://www.google.com"
    timeout = 5
    try:
        requests.get(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        return False

# Hàm đăng ký người dùng
def register_user(username, password, full_name):
    ref = db.reference(f'users/{username}')
    ref.set({
        "username": username,
        "password": password,  # Lưu mật khẩu dạng plain text (Không an toàn, chỉ nên làm cho bạn bè)
        "full_name": full_name
        # Không lưu highscore lúc đăng ký
    })
    print(f"Người dùng {username} đã được đăng ký thành công!")

# Hàm đăng nhập người dùng
def login_user(username, password):
    ref = db.reference(f'users/{username}')
    user_data = ref.get()
    
    if user_data and user_data['password'] == password:
        print(f"Đăng nhập thành công cho {username}")
        return True
    else:
        print(f"Đăng nhập thất bại: sai tên đăng nhập hoặc mật khẩu")
        return False

# Firebase handler để lưu trữ và lấy highscore
class FirebaseHandler:
    def __init__(self):
        self.username = None

    def login(self, username, password):
        if login_user(username, password):
            self.username = username
            return True
        return False

    def register(self, username, password, full_name):
        register_user(username, password, full_name)

    # Lưu điểm cao vào Firebase
    def save_highscore(self, score):
        if self.username:
            ref = db.reference(f'users/{self.username}/highscore')
            ref.set(score)
            print(f"Điểm cao {score} đã được lưu cho {self.username}")
        else:
            print("Chưa đăng nhập")

    # Lấy điểm cao nhất
    def get_highscore(self):
        if self.username:
            ref = db.reference(f'users/{self.username}/highscore')
            return ref.get()
        return 0

# Giao diện đăng nhập và đăng ký
class LoginWindow:
    def __init__(self, firebase):
        self.firebase = firebase
        self.root = Tk()
        self.root.title("Login")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        window_width = 400
        window_height = 300

        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)

        self.root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
        self.root.config(bg="lightgray")

        Label(self.root, text="Username", font=("Arial", 14), bg="lightgray").pack(pady=10)
        self.username_entry = Entry(self.root, font=("Arial", 14))
        self.username_entry.pack(pady=10)

        Label(self.root, text="Password", font=("Arial", 14), bg="lightgray").pack(pady=10)
        self.password_entry = Entry(self.root, font=("Arial", 14), show="*")
        self.password_entry.pack(pady=10)

        Button(self.root, text="Login", font=("Arial", 14), bg="green", fg="white", command=self.login).pack(pady=10)
        Button(self.root, text="Register", font=("Arial", 14), bg="blue", fg="white", command=self.register).pack(pady=10)

        self.root.mainloop()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if check_internet():
            if self.firebase.login(username, password):
                messagebox.showinfo("Success", "Đăng nhập thành công!")
                self.root.destroy()  # Đóng cửa sổ đăng nhập
                Menu(self.firebase)  # Mở menu sau khi đăng nhập thành công
            else:
                messagebox.showerror("Error", "Lỗi đăng nhập.")
        else:
            messagebox.showerror("Error", "Không có kết nối Internet.")

    def register(self):
        register_window = RegisterWindow(self.firebase)
        self.root.destroy()  # Đóng cửa sổ đăng nhập

class RegisterWindow:
    def __init__(self, firebase):
        self.firebase = firebase
        self.root = Tk()
        self.root.title("Register")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        window_width = 400
        window_height = 400

        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)

        self.root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
        self.root.config(bg="lightgray")

        Label(self.root, text="Username", font=("Arial", 14), bg="lightgray").pack(pady=10)
        self.username_entry = Entry(self.root, font=("Arial", 14))
        self.username_entry.pack(pady=10)

        Label(self.root, text="Password", font=("Arial", 14), bg="lightgray").pack(pady=10)
        self.password_entry = Entry(self.root, font=("Arial", 14), show="*")
        self.password_entry.pack(pady=10)

        Label(self.root, text="Full Name", font=("Arial", 14), bg="lightgray").pack(pady=10)
        self.full_name_entry = Entry(self.root, font=("Arial", 14))
        self.full_name_entry.pack(pady=10)

        Button(self.root, text="Register", font=("Arial", 14), bg="blue", fg="white", command=self.register).pack(pady=10)

        self.root.mainloop()

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        full_name = self.full_name_entry.get()

        if check_internet():
            self.firebase.register(username, password, full_name)
            messagebox.showinfo("Success", "Đăng ký thành công!")
            self.root.destroy()  # Đóng cửa sổ đăng ký
            LoginWindow(self.firebase)  # Quay lại màn hình đăng nhập
        else:
            messagebox.showerror("Error", "Không có kết nối Internet.")


# Firebase handler chính để quản lý đăng nhập, đăng ký, lưu trữ và lấy điểm số
class FirebaseHandler:
    def __init__(self):
        self.username = None

    def login(self, username, password):
        if login_user(username, password):
            self.username = username
            return True
        return False

    def register(self, username, password, full_name):
        register_user(username, password, full_name)

    # Lưu điểm cao vào Firebase
    def save_highscore(self, score):
        if self.username:
            ref = db.reference(f'users/{self.username}/highscore')
            ref.set(score)
            print(f"Điểm cao {score} đã được lưu cho {self.username}")
        else:
            print("Chưa đăng nhập")

    # Lấy điểm cao nhất
    def get_highscore(self):
        if self.username:
            ref = db.reference(f'users/{self.username}/highscore')
            return ref.get() or 0
        return 0

    # Đăng xuất người dùng (xóa thông tin trong phiên làm việc)
    def logout(self):
        self.username = None

# Giao diện đăng nhập và đăng ký
class LoginWindow:
    def __init__(self, firebase):
        self.firebase = firebase
        self.root = Tk()
        self.root.title("Login")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        window_width = 400
        window_height = 300

        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)

        self.root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
        self.root.config(bg="lightgray")

        Label(self.root, text="Username", font=("Arial", 14), bg="lightgray").pack(pady=10)
        self.username_entry = Entry(self.root, font=("Arial", 14))
        self.username_entry.pack(pady=10)

        Label(self.root, text="Password", font=("Arial", 14), bg="lightgray").pack(pady=10)
        self.password_entry = Entry(self.root, font=("Arial", 14), show="*")
        self.password_entry.pack(pady=10)

        Button(self.root, text="Login", font=("Arial", 14), bg="green", fg="white", command=self.login).pack(pady=10)
        Button(self.root, text="Register", font=("Arial", 14), bg="blue", fg="white", command=self.register).pack(pady=10)

        self.root.mainloop()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if check_internet():
            if self.firebase.login(username, password):
                messagebox.showinfo("Success", "Đăng nhập thành công!")
                self.root.destroy()  
                Menu(self.firebase)  # Gọi lớp Menu với firebase
            else:
                messagebox.showerror("Error", "Lỗi đăng nhập.")
        else:
            messagebox.showerror("Error", "Không có kết nối Internet.")

    def register(self):
        RegisterWindow(self.firebase)
        self.root.destroy()

class RegisterWindow:
    def __init__(self, firebase):
        self.firebase = firebase
        self.root = Tk()
        self.root.title("Register")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        window_width = 400
        window_height = 400

        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)

        self.root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
        self.root.config(bg="lightgray")

        Label(self.root, text="Username", font=("Arial", 14), bg="lightgray").pack(pady=10)
        self.username_entry = Entry(self.root, font=("Arial", 14))
        self.username_entry.pack(pady=10)

        Label(self.root, text="Password", font=("Arial", 14), bg="lightgray").pack(pady=10)
        self.password_entry = Entry(self.root, font=("Arial", 14), show="*")
        self.password_entry.pack(pady=10)

        Label(self.root, text="Full Name", font=("Arial", 14), bg="lightgray").pack(pady=10)
        self.full_name_entry = Entry(self.root, font=("Arial", 14))
        self.full_name_entry.pack(pady=10)

        Button(self.root, text="Register", font=("Arial", 14), bg="blue", fg="white", command=self.register).pack(pady=10)

        self.root.mainloop()

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        full_name = self.full_name_entry.get()

        if check_internet():
            self.firebase.register(username, password, full_name)
            messagebox.showinfo("Success", "Đăng ký thành công!")
            self.root.destroy()  # Đóng cửa sổ đăng ký
            LoginWindow(self.firebase)  # Quay lại màn hình đăng nhập
        else:
            messagebox.showerror("Error", "Không có kết nối Internet.")
class Board:
    bg_color = {
        '2': '#eee4da',
        '4': '#ede0c8',
        '8': '#edc850',
        '16': '#edc53f',
        '32': '#f67c5f',
        '64': '#f65e3b',
        '128': '#edcf72',
        '256': '#edcc61',
        '512': '#f2b179',
        '1024': '#f59563',
        '2048': '#edc22e',
    }
    color = {
        '2': '#776e65',
        '4': '#f9f6f2',
        '8': '#f9f6f2',
        '16': '#f9f6f2',
        '32': '#f9f6f2',
        '64': '#f9f6f2',
        '128': '#f9f6f2',
        '256': '#f9f6f2',
        '512': '#776e65',
        '1024': '#f9f6f2',
        '2048': '#f9f6f2',
    }
    def __init__(self, size=4, firebase=None):
        self.n = size
        self.size = size
        self.firebase = firebase  # Thêm firebase vào đối tượng Board
        self.window = Tk()
        self.window.title('VAA 2048')
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        window_width = 550
        window_height = 600

        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)

        self.window.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
        self.window.config(bg="lightgray")

        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        self.score_label = Label(self.window, text="Score: 0", font=('arial', 24), bg="lightgray")
        self.score_label.grid(row=0, column=0, pady=(20, 10), sticky="n")

        # Thêm nút Reset và Quay về Menu
        button_frame = Frame(self.window, bg="lightgray")
        button_frame.grid(row=2, column=0, pady=10)

        self.reset_button = Button(button_frame, text="Reset", command=self.reset_game, font=('arial', 14), bg="orange", fg="white", width=8)
        self.reset_button.grid(row=0, column=0, padx=10)

        self.menu_button = Button(button_frame, text="Menu", command=self.back_to_menu, font=('arial', 14), bg="green", fg="white", width=8)
        self.menu_button.grid(row=0, column=1, padx=10)

        # Khung chứa bảng game
        self.gameArea = Frame(self.window, bg='azure3')
        self.gameArea.grid(row=1, column=0, pady=20, sticky="nsew")

        self.board = []
        self.gridCell = [[0] * self.size for _ in range(self.size)]
        self.compress = False
        self.merge = False
        self.moved = False
        self.score = 0

        for i in range(self.size):
            rows = []
            for j in range(self.size):
                l = Label(self.gameArea, text='', bg='azure4', font=('arial', 22, 'bold'), width=4, height=2)
                l.grid(row=i, column=j)
                rows.append(l)
            self.board.append(rows)

        for i in range(self.size):
            self.gameArea.grid_rowconfigure(i, weight=1)
            self.gameArea.grid_columnconfigure(i, weight=1)

    def reverse(self):
        for ind in range(self.size):
            self.gridCell[ind] = self.gridCell[ind][::-1]

    def transpose(self):
        self.gridCell = [list(t) for t in zip(*self.gridCell)]

    def compressGrid(self):
        self.compress = False
        temp = [[0] * self.size for _ in range(self.size)]
        for i in range(self.size):
            cnt = 0
            for j in range(self.size):
                if self.gridCell[i][j] != 0:
                    temp[i][cnt] = self.gridCell[i][j]
                    if cnt != j:
                        self.compress = True
                    cnt += 1
        self.gridCell = temp

    def mergeGrid(self):
        self.merge = False
        for i in range(self.size):
            for j in range(self.size - 1):
                if self.gridCell[i][j] == self.gridCell[i][j + 1] and self.gridCell[i][j] != 0:
                    self.gridCell[i][j] *= 2
                    self.gridCell[i][j + 1] = 0
                    self.score += self.gridCell[i][j]
                    self.merge = True
                    self.update_score()

    def random_cell(self):
        cells = []
        for i in range(self.size):
            for j in range(self.size):
                if self.gridCell[i][j] == 0:
                    cells.append((i, j))
        if cells:
            curr = random.choice(cells)
            i = curr[0]
            j = curr[1]
            self.gridCell[i][j] = 2

    def can_merge(self):
        for i in range(self.size):
            for j in range(self.size - 1):
                if self.gridCell[i][j] == self.gridCell[i][j + 1]:
                    return True

        for i in range(self.size - 1):
            for j in range(self.size):
                if self.gridCell[i + 1][j] == self.gridCell[i][j]:
                    return True
        return False

    def paintGrid(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.gridCell[i][j] == 0:
                    self.board[i][j].config(text='', bg='azure4')
                else:
                    self.board[i][j].config(text=str(self.gridCell[i][j]), bg=self.bg_color.get(str(self.gridCell[i][j]), 'azure4'), fg=self.color.get(str(self.gridCell[i][j]), 'black'))

    def update_score(self):
        self.score_label.config(text=f"Score: {self.score}")

    def reset_game(self):
        self.gridCell = [[0] * self.size for _ in range(self.size)]
        self.score = 0
        self.update_score()
        self.random_cell()
        self.random_cell()
        self.paintGrid()

    def back_to_menu(self):
        self.window.destroy()  # Đóng cửa sổ trò chơi hiện tại
        if self.firebase:  # Đảm bảo rằng firebase không phải là None
            Menu(self.firebase)  # Gọi lớp Menu với firebase
        else:
            print("Firebase instance not found!")


class Game:
    def __init__(self, gamepanel, firebase):
        self.gamepanel = gamepanel
        self.firebase = firebase
        self.end = False
        self.won = False
        self.current_score = 0
        self.highscore = self.firebase.get_highscore()  # Lấy điểm cao nhất từ Firebase

    def end_game(self):
        self.end = True
        self.save_highscore()  # Lưu điểm cao khi kết thúc trò chơi
        self.show_custom_message("Game Over", "You lost! Do you want to play again?", self.gamepanel.reset_game)

    def save_highscore(self):
        # So sánh và lưu điểm cao nếu điểm hiện tại cao hơn
        if self.gamepanel.score > self.highscore:
            self.highscore = self.gamepanel.score
            self.firebase.save_highscore(self.highscore)
            print(f"New highscore saved: {self.highscore}")
        else:
            print(f"Highscore remains: {self.highscore}")

    def show_win_message(self):
        self.save_highscore()  # Lưu điểm cao khi chiến thắng
        self.show_custom_message("You Win", "Congratulations! You reached 2048!\nDo you want to play again?", self.gamepanel.reset_game)

    def show_custom_message(self, title, message, reset_command):
        message_window = Toplevel(self.gamepanel.window)
        message_window.title(title)

        window_width = 300
        window_height = 150
        screen_width = self.gamepanel.window.winfo_screenwidth()
        screen_height = self.gamepanel.window.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        message_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
        message_window.config(bg="lightgray")

        # Nhãn thông báo
        message_label = Label(message_window, text=message, font=('Arial', 14), bg="lightgray", fg="black")
        message_label.pack(pady=20)

        # Nút "Play Again"
        play_again_button = Button(message_window, text="Play Again", font=('Arial', 12, 'bold'),
                                   bg="green", fg="white", command=lambda: self.reset_game(message_window, reset_command))
        play_again_button.pack(side=LEFT, padx=20, pady=10)

        # Nút "Exit"
        exit_button = Button(message_window, text="Exit", font=('Arial', 12, 'bold'),
                             bg="red", fg="white", command=lambda: self.close_game(message_window))
        exit_button.pack(side=RIGHT, padx=20, pady=10)

    def reset_game(self, message_window, reset_command):
        message_window.destroy()
        reset_command()

    def close_game(self, message_window):
        message_window.destroy()
        self.gamepanel.window.destroy()
        Menu(self.firebase)

    def start(self):
        self.gamepanel.random_cell()
        self.gamepanel.random_cell()
        self.gamepanel.paintGrid()
        self.gamepanel.window.bind('<Key>', self.link_keys)
        self.update_highscore_label()  # Hiển thị điểm cao nhất
        self.gamepanel.window.mainloop()

    def update_highscore_label(self):
        # Cập nhật hiển thị điểm cao nhất trên màn hình
        self.highscore_label = Label(self.gamepanel.window, text=f"Highscore: {self.highscore}", font=('Arial', 14), bg="lightgray")
        self.highscore_label.grid(row=0, column=1, padx=10, pady=10)

    def link_keys(self, event):
        if self.end or self.won:
            return

        self.gamepanel.compress = False
        self.gamepanel.merge = False
        self.gamepanel.moved = False

        presed_key = event.keysym

        if presed_key == 'Up':
            self.gamepanel.transpose()
            self.gamepanel.compressGrid()
            self.gamepanel.mergeGrid()
            self.gamepanel.moved = self.gamepanel.compress or self.gamepanel.merge
            self.gamepanel.compressGrid()
            self.gamepanel.transpose()

        elif presed_key == 'Down':
            self.gamepanel.transpose()
            self.gamepanel.reverse()
            self.gamepanel.compressGrid()
            self.gamepanel.mergeGrid()
            self.gamepanel.moved = self.gamepanel.compress or self.gamepanel.merge
            self.gamepanel.compressGrid()
            self.gamepanel.reverse()
            self.gamepanel.transpose()

        elif presed_key == 'Left':
            self.gamepanel.compressGrid()
            self.gamepanel.mergeGrid()
            self.gamepanel.moved = self.gamepanel.compress or self.gamepanel.merge
            self.gamepanel.compressGrid()

        elif presed_key == 'Right':
            self.gamepanel.reverse()
            self.gamepanel.compressGrid()
            self.gamepanel.mergeGrid()
            self.gamepanel.moved = self.gamepanel.compress or self.gamepanel.merge
            self.gamepanel.compressGrid()
            self.gamepanel.reverse()

        self.gamepanel.paintGrid()
        print("Current Score:", self.gamepanel.score)

        flag = 0
        for i in range(4):
            for j in range(4):
                if self.gamepanel.gridCell[i][j] == 2048:
                    flag = 1
                    break

        if flag == 1:
            self.won = True
            self.show_win_message()
            return

        for i in range(4):
            for j in range(4):
                if self.gamepanel.gridCell[i][j] == 0:
                    flag = 1
                    break

        if not (flag or self.gamepanel.can_merge()):
            self.end_game()

        if self.gamepanel.moved:
            self.gamepanel.random_cell()

        self.gamepanel.paintGrid()

class Leaderboard:
    def __init__(self, firebase):
        self.firebase = firebase
        self.root = Tk()
        self.root.title("Bảng Xếp Hạng")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        window_width = 500
        window_height = 400

        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)

        self.root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
        self.root.config(bg="lightgray")

        title_label = Label(self.root, text="Bảng Xếp Hạng", font=('Arial', 24, 'bold'), bg="lightgray", fg="black")
        title_label.pack(pady=20)

        self.leaderboard_frame = Frame(self.root, bg="white")
        self.leaderboard_frame.pack(fill=BOTH, expand=True)

        self.show_leaderboard()

        close_button = Button(self.root, text="Quay lại", font=('Arial', 12, 'bold'), bg="red", fg="white", command=self.back_to_menu)
        close_button.pack(pady=10)

        self.root.mainloop()

    def show_leaderboard(self):
    # Lấy dữ liệu từ Firebase và sắp xếp theo điểm cao nhất
        users_ref = db.reference('users')
        users = users_ref.get()

        # Tạo danh sách xếp hạng với số thứ tự, tên và điểm cao
        if users:
            sorted_users = sorted(users.items(), key=lambda x: x[1].get('highscore', 0), reverse=True)
            
            for index, (user_id, data) in enumerate(sorted_users, start=1):
                full_name = data.get('full_name', 'Unknown')
                highscore = data.get('highscore', 0)  # Lấy giá trị 'highscore' hoặc mặc định là 0

                leaderboard_label = Label(self.leaderboard_frame, text=f"{index}. {full_name} - {highscore} điểm", font=('Arial', 14), bg="white", fg="black")
                leaderboard_label.pack(anchor=W, padx=20, pady=5)
        else:
            no_data_label = Label(self.leaderboard_frame, text="Không có dữ liệu bảng xếp hạng", font=('Arial', 14), bg="white", fg="black")
            no_data_label.pack(anchor=W, padx=20, pady=5)


    def back_to_menu(self):
        self.root.destroy()
        Menu(self.firebase)


class Menu:
    def __init__(self, firebase):
        self.firebase = firebase  # Đảm bảo firebase được lưu ở đây
        self.root = Tk()
        self.root.title('2048 Menu')
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        window_width = 550
        window_height = 560

        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)

        self.root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
        self.root.config(bg="lightblue")

        self.menu_frame = Frame(self.root, bg="lightblue")
        self.menu_frame.pack(pady=20)

        self.title_label = Label(self.menu_frame, text='Game 2048!', font=('Arial', 28, 'bold'), bg="lightblue",
                                 fg="darkblue")
        self.title_label.pack(pady=20)
        
        self.title_label = Label(self.menu_frame, text=f'Welcome, {self.firebase.username}!', font=('Arial', 28, 'bold'), bg="lightblue",
                                 fg="darkblue")
        self.title_label.pack(pady=20)

        self.highscore_label = Label(self.menu_frame, text=f"Highscore: {self.firebase.get_highscore()}", font=('Arial', 18), bg="lightblue")
        self.highscore_label.pack(pady=10)

        self.size_label = Label(self.menu_frame, text='Select Board Size:', font=('Arial', 18), bg="lightblue", fg="black")
        self.size_label.pack(pady=10)

        self.size_var = StringVar(value='4')
        self.size_4 = Radiobutton(self.menu_frame, text='4x4', variable=self.size_var, value='4', font=('Arial', 14),
                                  bg="lightblue")
        self.size_4.pack(pady=5)
        self.size_5 = Radiobutton(self.menu_frame, text='5x5', variable=self.size_var, value='5', font=('Arial', 14),
                                  bg="lightblue")
        self.size_5.pack(pady=5)

        self.start_button = Button(self.menu_frame, text='Start Game', font=('Arial', 14, 'bold'), command=self.start_game,
                                   bg="green", fg="white", width=15, height=2)
        self.start_button.pack(pady=20)

        self.help_button = Button(self.menu_frame, text='Help', font=('Arial', 12), command=self.show_help, bg="orange",
                                  fg="white", width=12, height=1)
        self.help_button.pack(pady=10)

        self.team_button = Button(self.menu_frame, text='Team Members', font=('Arial', 12), command=self.show_team,
                                  bg="purple", fg="white", width=12, height=1)
        self.team_button.pack(pady=10)
        
        self.leaderboard_button = Button(self.menu_frame, text='Bảng Xếp Hạng', font=('Arial', 14, 'bold'), command=self.show_leaderboard,
                                         bg="blue", fg="white", width=15, height=2)
        self.leaderboard_button.pack(pady=10)


        Button(self.menu_frame, text="Logout", font=('Arial', 12), command=self.logout, bg="red", fg="white", width=12, height=1).pack(pady=10)

        self.root.mainloop()

    def show_leaderboard(self):
        self.root.destroy()  # Đóng menu hiện tại
        Leaderboard(self.firebase)  # Mở màn hình bảng xếp hạng
    
    def logout(self):
        # Đóng cửa sổ hiện tại và quay về màn hình đăng nhập
        self.root.destroy()
        LoginWindow(self.firebase)

    def start_game(self):
        size = int(self.size_var.get())
        self.root.destroy()  # Đóng cửa sổ menu
        gamepanel = Board(size, self.firebase)  # Truyền firebase vào Board
        game2048 = Game(gamepanel, self.firebase)
        game2048.start()

    def show_help(self):
        help_window = Toplevel(self.root)
        help_window.title("Help")

        window_width = 550
        window_height = 500
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        help_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
        help_window.config(bg="lightblue")

        title_label = Label(help_window, text="How to Play", font=('Arial', 18, 'bold'), bg="lightgray", fg="black")
        title_label.pack(pady=10)

        help_text = """
        Sử dụng các phím mũi tên để di chuyển các ô. 
        Kết hợp các ô có cùng số để đạt 2048!
        Chúc may mắn!
        """
        help_label = Label(help_window, text=help_text, font=('Arial', 14), bg="lightgray", fg="black", justify=LEFT)
        help_label.pack(pady=10)


        close_button = Button(help_window, text="Close", font=('Arial', 12, 'bold'), bg="red", fg="white",
                              command=help_window.destroy)
        close_button.pack(pady=20)

    def show_team(self):
        team_window = Toplevel(self.root)
        team_window.title("Team Members")

        window_width = 300
        window_height = 280
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        team_window.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
        team_window.config(bg="lightblue")

        title_label = Label(team_window, text="Team Members", font=('Arial', 18, 'bold'), bg="lightblue", fg="darkblue")
        title_label.pack(pady=10)

        team_info = Label(team_window, text="Thành viên nhóm:\nVõ Minh Chí - 2254810136\nLê Anh Quốc - 2254810151\nTôn Thất Kha - 2254810111\nTrần Minh Tâm - 2254810119\nPhạm Dương Hưng - 2254810122", font=('Arial', 14),
                          bg="lightblue", fg="black")
        team_info.pack(pady=10)

        close_button = Button(team_window, text="Close", font=('Arial', 12, 'bold'), bg="red", fg="white",
                              command=team_window.destroy)
        close_button.pack(pady=20)

    def logout(self):
        self.firebase.logout()
        self.root.destroy()
        LoginWindow(self.firebase)

# Hàm kiểm tra kết nối internet
def check_internet():
    url = "http://www.google.com"
    timeout = 5
    try:
        requests.get(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        return False

# Khởi chạy ứng dụng
if __name__ == '__main__':
    firebase_handler = FirebaseHandler()
    if check_internet():
        LoginWindow(firebase_handler)
    else:
        messagebox.showerror("Error", "Không có kết nối Internet.")


