import win32gui
import win32ui
import win32con
import win32api
import win32process
from PIL import Image
import ctypes
import os

class MapleLandWindowManager:
    def __init__(self, window_title="MapleLand"):
        self.window_title = window_title
        self.hwnd = None
        
        # 제외할 브라우저 프로세스 및 클래스명
        self.blacklist_processes = [
            "chrome.exe", "msedge.exe", "firefox.exe", 
            "whale.exe", "opera.exe", "brave.exe", "iexplore.exe"
        ]
        self.blacklist_classes = [
            "Chrome_WidgetWin_1", "MozillaWindowClass", "IEFrame"
        ]
        # 허용할 게임 프로세스 키워드 (MapleStory Worlds 등)
        self.whitelist_process_keywords = ["MapleStoryWorlds", "MapleLand"]

        # DPI 인식을 설정하여 정확한 좌표를 가져옵니다.
        try:
            # Windows 8.1 이상 (PROCESS_PER_MONITOR_DPI_AWARE = 2)
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                # Windows Vista 이상
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

    def find_window(self):
        """MapleLand 창 핸들을 찾고 검증합니다."""
        target_hwnd = None
        
        def enum_cb(hwnd, results):
            if self.window_title in win32gui.GetWindowText(hwnd):
                if self.is_valid_game_window(hwnd):
                    results.append(hwnd)
        
        results = []
        win32gui.EnumWindows(enum_cb, results)
        
        if results:
            # 여러 개가 발견되면 첫 번째 검증된 창을 선택
            self.hwnd = results[0]
            return self.hwnd
        
        self.hwnd = None
        return None

    def is_valid_game_window(self, hwnd):
        """해당 윈도우가 실제 게임 클라이언트인지 검증합니다."""
        try:
            # 1. 클래스명 검사
            class_name = win32gui.GetClassName(hwnd)
            if any(bc in class_name for bc in self.blacklist_classes):
                return False

            # 2. 프로세스 정보 검사
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid)
            
            # 프로세스 실행 파일 경로 가져오기
            exe_path = win32process.GetModuleFileNameEx(handle, 0)
            win32api.CloseHandle(handle)
            
            exe_name = os.path.basename(exe_path).lower()
            
            # 블랙리스트(브라우저 등) 포함 여부 확인
            if any(bp in exe_name for bp in self.blacklist_processes):
                return False
            
            # 화이트리스트 키워드 확인 (권장)
            if any(wp.lower() in exe_name for wp in self.whitelist_process_keywords):
                return True

            # 특별한 키워드가 없더라도 브라우저가 아니라면 일단 허용 (필요에 따라 엄격하게 수정 가능)
            return True
        except Exception as e:
            # 권한 문제 등으로 정보를 가져올 수 없는 경우 기본적으로 가짜일 가능성이 높다고 판단
            return False

    def get_window_rect(self):
        """창의 절대 좌표 (Left, Top, Right, Bottom)를 반환합니다."""
        if not self.hwnd:
            return None
        return win32gui.GetWindowRect(self.hwnd)

    def is_minimized(self):
        """창이 최소화 상태인지 확인합니다."""
        if not self.hwnd:
            return True
        return win32gui.IsIconic(self.hwnd)

    def capture(self):
        """창 영역만 캡처하여 PIL Image로 반환합니다."""
        if not self.hwnd:
            if not self.find_window():
                raise Exception(f"'{self.window_title}' 창을 찾을 수 없습니다.")

        if self.is_minimized():
            raise Exception("창이 최소화되어 있어 캡처할 수 없습니다.")

        # 창 크기 가져오기
        left, top, right, bottom = self.get_window_rect()
        width = right - left
        height = bottom - top

        # 윈도우 DC 확보
        hwnd_dc = win32gui.GetWindowDC(self.hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()

        # 비트맵 생성
        save_bit_map = win32ui.CreateBitmap()
        save_bit_map.CreateCompatibleBitmap(mfc_dc, width, height)
        save_dc.SelectObject(save_bit_map)

        # PrintWindow를 사용하여 캡처 (다른 창에 가려져도 어느 정도 가능)
        # result가 0이면 실패, 1이면 성공
        result = ctypes.windll.user32.PrintWindow(self.hwnd, save_dc.GetSafeHdc(), 2) # PW_RENDERFULLCONTENT = 2

        if result != 1:
            # PrintWindow 실패 시 BitBlt 시도 (하지만 가려진 부분은 캡처 안됨)
            save_dc.BitBlt((0, 0), (width, height), mfc_dc, (0, 0), win32con.SRCCOPY)

        # 비트맵 정보를 바탕으로 PIL Image 생성
        bmp_info = save_bit_map.GetInfo()
        bmp_str = save_bit_map.GetBitmapBits(True)
        
        img = Image.frombuffer(
            'RGB',
            (bmp_info['bmWidth'], bmp_info['bmHeight']),
            bmp_str, 'raw', 'BGRX', 0, 1
        )

        # 리소스 해제
        win32gui.DeleteObject(save_bit_map.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, hwnd_dc)

        return img

if __name__ == "__main__":
    # 간단한 테스트 로직
    manager = MapleLandWindowManager()
    hwnd = manager.find_window()
    if hwnd:
        print(f"Found window: {hwnd}")
        try:
            image = manager.capture()
            image.save("debug_capture.png")
            print("Capture saved to debug_capture.png")
        except Exception as e:
            print(f"Capture failed: {e}")
    else:
        print("Window not found.")
