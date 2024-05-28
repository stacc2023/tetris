import ctypes
import time

# # 콘솔 출력 핸들 가져오기
STD_OUTPUT_HANDLE = -11
console_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

def move(x, y):
    pos = ctypes.wintypes._COORD(x, y)
    ctypes.windll.kernel32.SetConsoleCursorPosition(console_handle, pos)

# COORD 구조체 정의
class COORD(ctypes.Structure):
    _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

# 콘솔 화면 버퍼 정보 구조체 정의
class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
    _fields_ = [
        ("dwSize", COORD),
        ("dwCursorPosition", COORD),
        ("wAttributes", ctypes.c_ushort),
        ("srWindow", ctypes.wintypes.SMALL_RECT),
        ("dwMaximumWindowSize", COORD),
    ]

# 현재 커서 위치 얻기 함수
def get_cursor_position():
    csbi = CONSOLE_SCREEN_BUFFER_INFO()
    ctypes.windll.kernel32.GetConsoleScreenBufferInfo(console_handle, ctypes.byref(csbi))
    return csbi.dwCursorPosition.X, csbi.dwCursorPosition.Y

# def clear_screen():
#     ctypes.windll.kernel32.FillConsoleOutputCharacterA(console_handle, ctypes.c_char(b' '), 80*25, ctypes.wintypes._COORD(0, 0), ctypes.byref(ctypes.wintypes.DWORD()))
#     set_cursor_position(0, 0)

# def print_at_position(x, y, text):
#     set_cursor_position(x, y)
#     print(text, end='', flush=True)